###我的需求

Please modify the ‘Version_1.py’:
1. Do not import vector files and table_wireframe files for header separators
2. Import the mechanical vector diagram to the vector file
3. A table wireframe is a rectangle which has at least 2 rows and 2 columns, separated by Bond lines thick or Grid lines.
All wireframes of the table, including Bond lines（these are typically thicker）and  Grid lines（typically thinner and shorter）, should be imported into the table_wireframe file
4. Please refer to ‘version_2.py’  to export the text in the table to ‘combined_table.csv’:
‘Version_2.py’ accurately exports all the text in the table to the ‘combined_table_1_to_13.csv’ file, only the text in the table, and does not include the other text in the pdf file,accurately.
For clarity, please insert a blank line between every 2 tables.
5. Please refer to ‘version_3.py’ to export all jpg images:
‘Version_3.py’ export all jpg images If there is a large image composed of many small images on one page, combine these small images into a large image and export this large picture
; If there are multiple separate graphs on one page, export these jpgs separately;accurately.
6.Please export the text in the pdf file to the content.txt, note: do not import the text in the table, do not import the text in the header.

###’Version_1.py’
Version_1.py exports table_wireframe and vector files with:
(1) Pages 1 and 13 export the vector file with the header divider.
(2) The vector.svg are exported on pages 3 and 5, and the content of the file is all the wireframes of the table on this page (including the 2 bond lines in the wireframe), and the header divider is included;
(3) On page 9, the page_9_vector.svg is exported, and the content of the file is all the wireframes of the table (the wireframes of the table on this page do not have bond lines), and the header divider is added;
(4) Pages 2, 4, 6, 7, 8, 11, and 13 all export table_wireframe.svg files and vector.svg files, where:
The content of the table_wireframe is the bond line in the table wireframe with there are more than 3 lines;
The content of the vector is all wireframes of the table except for the bond line, and it has a header divider;
(5) Page 10 exports the ‘page_10_table_wireframe.svg’ and ‘page_10_vector.svg’, where:
The content of the ‘page_10_table_wireframe.svg’’ is a mechanical vector illustration,
‘page_10_vector.svg’’ are all the wireframes of the table (the wireframes of this table have no bond line) and have a header divider;

###’Version_2.py’
 ’Version_2.py’ exported:
1. All jpg pictures, accurate;
2. ‘combined_table_1_to_13.csv’: The text in all forms is accurate;
3. Each page exports 1 vector file, where:
(1) The content of pages 1 and 13 is the header divider, and the other pages also import the header divider;
(2) On page 10, the table wireframe is exported, with the header divider, and the vector art is not included;
(3) All table wireframes are exported for the other pages, including bond lines, with header dividers.

###’Version_3.py’  exported:
1. Exported jpg file: If there is a large picture composed of many small pictures on a page, combine these small pictures into a large picture and export this large picture ; If there are multiple separate graphs on one page, export these jpgs separately;
2. ‘content.txt’: All text in the PDF file, including the text in the form;
3. The vector file is exported, where:
(1) There are no export files on pages 1 and 13;
(2) On page 10, the table wireframe is exported, without the mechanical vector illustration, and the header divider is included;
(3) All table wireframes including bond lines are exported for other pages, and header dividers are included;