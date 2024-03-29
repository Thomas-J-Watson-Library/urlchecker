@ECHO OFF
ScreamingFrogSEOSpiderCli.exe --crawl-list %1 --headless --save-crawl --overwrite --export-format "csv" --output-folder "data" --export-tabs "Response Codes:All"
cd data
set orig_name=%1
set file_name=%orig_name:*\=%
set new_name=res_%file_name%
rename  response_codes_all.csv %new_name%
del crawl.seospider
