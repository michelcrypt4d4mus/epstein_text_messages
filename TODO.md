1. Download and OCR the missing data sets (currently have 1, 3, 4, 5, 6, 7, 9, 12)
2. Turn `DojFile` objects that are emails into proper `Email` objectst with all the header repair and timestamp etc. parsing that entails
3. Add more particularly interesting DOJ file IDs to `INTERESTING_DOJ_FILES`
4. Find a better heuristic to exclude garbage OCR files from the `DojFile` collection and/or mark problematic files in `BAD_DOJ_FILE_IDS`
5. Identify dupes in the DOJ files
6. Reformat `DojFile` objects to remove the box around them (saves a lot of whitespace in the HTML)
7. Identify and attribute redacted emails in the DOJ files
