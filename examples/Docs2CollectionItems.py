from treillage import Treillage, TreillageHTTPException, TreillageRateLimitException
import asyncio
import pandas
import progressbar
import json
import copy


async def main():
    # path to credentials file
    credentials_file = "creds.yml"
    # path to spreadsheet with data for the script
    filename = "Docs2CollectionItems.xlsx"
    # Use pandas to read an excel spreadsheet into a dataframe
    batch = pandas.read_excel(filename, na_filter=False)
    # Setup a progress bar that will display in the console
    widgets = [
        ' (', progressbar.SimpleProgress(),
        ' ', progressbar.Percentage(), ') ',
        progressbar.Bar(),
        ' [', progressbar.Timer(), '] ',
    ]
    # Create the progress bar
    with progressbar.ProgressBar(max_value=len(batch), widgets=widgets) as bar:
        # Create the treillage context manager
        async with Treillage(credentials_file, rate_limit_max_tokens=8, rate_limit_token_regen_rate=8) as fv:
            # Iterate over every row in the spreadsheet
            for idx, row in batch.iterrows():
                # Process the data from the row
                await handle_document(fv=fv,
                                      projectid=row["__ProjectID"],
                                      sectionselector=row["SectionSelector"],
                                      collectionid=row["__CollectionItemGuid"],
                                      fieldselector=row["FieldSelector"],
                                      docids=json.loads(row["JSON__DocIDs"])
                                      )
                # Update the position of the progress bar
                bar.update(idx)


async def handle_document(fv, projectid, sectionselector, collectionid, fieldselector, docids):
    # Set the endpoint that will be requested
    endpoint = f'/core/projects/{projectid}/collections/{sectionselector}/{collectionid}'
    # Format parameters for the log file
    log_data = f'{projectid}\t{sectionselector}\t{fieldselector}\t{collectionid}\t{docids}'
    # Use a try-except block to handle errors
    try:
        # get fieldselector info about the requested collection
        resp = await fv.conn.get(endpoint=endpoint, params={'requestedFields': fieldselector})
        # create a deep copy of the dictionary so nested data can be edited separate from the original values
        newdocids = copy.deepcopy(docids)

        # If needed, update docIDs based on the data returned from the GET request
        if fieldselector in resp["dataObject"].keys() and len(resp["dataObject"][fieldselector]) > 0:
            requestedfield = resp["dataObject"][fieldselector]
            newdocids["dataObject"][fieldselector] = newdocids["dataObject"][fieldselector] + requestedfield
        # Update formatted log data with new values
        log_data = log_data + "\t" + str(newdocids)
        # Patch the collection item with the additional docIDs
        await patch_collection_item(fv, endpoint, newdocids, log_data)

    # Retry if the GET request was rate-limited
    except TreillageRateLimitException:
        await handle_document(fv, projectid, sectionselector, collectionid, fieldselector, docids)
    # Log all other failed GET requests
    except TreillageHTTPException as e:
        with open("error.txt", "a") as out:
            out.write(f"{e.code}\t{log_data}\t{''}\t{e.msg}\tFailed to Get\n")


async def patch_collection_item(fv, endpoint, json, log_data):
    try:
        # make the patch request
        await fv.conn.patch(endpoint=endpoint, json=json)
        # log the successful update
        with open("result.txt", "a") as out:
            out.write(f"200\t{log_data}\n")
    # Retry if the PATCH request was rate-limited
    except TreillageRateLimitException:
        await patch_collection_item(fv, endpoint, json, log_data)
    # Log all other failed PATCH requests
    except TreillageHTTPException as e:
        with open("error.txt", "a") as out:
            out.write(f"{e.code}\t{log_data}\t{e.msg}\tFailed to Patch\n")


if __name__ == "__main__":
    asyncio.run(main())
