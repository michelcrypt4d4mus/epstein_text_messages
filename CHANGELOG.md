# NEXT RELEASE
* Include a compressed pickle file with all the archived data in this repo
* `--load-new` option to scan for only new files
* `--output-chrono` option to print all file types intermingled in chronological order

### 1.6.1
* site index at top that cross links all sites
* internal section links on `CURATED` page
* `Category` enum

# 1.6.0
* Rework the way the various generated HTML pages link to each other, update header to reflect it
* Rename `DocLocation` to `FileInfo` and delegate things like `file_size` to it

### 1.5.7
* Move all URL and file path / name / etc. functionality to `DocLocation` class

### 1.5.6

### 1.5.5
* Also copy properties to duplicate docs that aren't emails
* Improve the categorization logic in `DocCfg`

### 1.5.4
* Document configs (`DocCfg`, `EmailCfg`, etc) are no longer saved with the pickled data. Some configs are derived on the fly.
* Add `uncertain_reason` to `DocCfg` and `recipient_uncertain` to `CommunicationCfg`, show question marks in info sentence next to uncertain recipients

### 1.5.3

### 1.5.2
* `ContactInfo` class to unify regexes and biographical info
* `epstein_generate` new option `--reload-doj` option to reload DOJ January 2026 files (skips reloading HOUSE_OVERSIGHT files)
* `epstein_show` new options `--open-txt`, `--open-pdf`, `--open-both`, `--open-url`, `--open-jmail`
* lots of color highlighting and identification of DOJ 2026-01-30 files

### 1.5.1
* Integrate DOJ file emails into the normal email generation
* Include a pre-packaged `the_epstein_files.pkl.gz` in the repo

# 1.5.0
* Add support for DOJ Epstein Files Transparency Act documents via `DojFile` class
* `--output-doj-files` option to print Epstein Files Transparency Act documents

### 1.4.1
* Use `inkscape` instead of `cairosvg` for .png emailers table generation

# 1.4.0
* Rename `epstein_search` to `epstein_grep`
* `--email-body` argument
* `EmailHeader.reply_to` field

# 1.3.0
* `--constantize` debug option
* Unify all email config properties in `EmailCfg` objects

### 1.2.6

### 1.2.5
* `--write-text` option

### 1.2.4
* Linkify links in emails

### 1.2.3

### 1.2.2
* Internal links

### 1.2.1

# 1.2.0
* PNG export of emailers table

### 1.1.5

### 1.1.4

### 1.1.3

### 1.1.2
* Use a table for emailers in all cases, remove email tables

### 1.1.1
* Remove AM/PM from imessage timestamp strings

# 1.1.0
* Chronological emails page

### 1.0.16

### 1.0.15

### 1.0.14

### 1.0.13

### 1.0.12

### 1.0.11
* Extract configs
* phone numbers

### 1.0.10

### 1.0.9
* Fix import

### 1.0.8
* Add `rich-argparse-plus`

### 1.0.7
* Fix image for pypi

### 1.0.6
* Add `epstein_word_count` script
* Add `--output-json-files` option
* Deploy the collected JSON files at https://michelcrypt4d4mus.github.io/epstein_text_messages/json_files_from_epstein_files_nov_2025.json

### 1.0.5
* Remove `--pickled` argument

### 1.0.4

### 1.0.3
* Metadata ordering

##### 1.0.2
* Add `epstein_show`, `epstein_search`, `epstein_generate` scripts

### 1.0.1
* Improvements
