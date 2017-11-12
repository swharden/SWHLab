## CJFdecimateWKS

`cjfdecimatewks [decimate by]`

Reduces data vertically by making each cell the average of a given number of rows. Standard deviation is not calculated. This is done in place and destructively modifies the selected worksheet.

**Examples:**
* `cjfdecimatewks 10` _makes each row the average of 10 original rows_ 

## ReadTags

`readtags`, `readtags 1`

Shows the sweep number and time for tags in the loaded ABF. `readtags 1` draws vertical lines on the selected graph window (assuming horizontal time scale is in minutes).

## SetPath
`setpath`, `setpath "C:\path\to\file.abf"`, `setpath wks`

Load an ABF file into the ABFGraph window. Without an argument it opens a dialog box. If given a valid file path (as a string in qutoes), it loads a specific file.

`setpath wks` will load the ABF which was analyzed to produce data on the currently-selected worksheet. If that ABF file cannot be found, an ABF file with the same name will be sought in an alternative folder defined in the labtalk variable altPath, which can be set from the command window by `altPath$="C:\alternate\folder"`

## AddX
`addx`, `addx 1/60`

Replaces the first column of the selected worksheet with an ascending series of numbers. If an argument is given, each number is multiplied by the argument.

## BaseToRange
`BaseToRange [column] [time start] [time end]`

Assuming the first column is in time units, determines the average value of a certain column between a range of time units, then subtract that value from the entire column. This is "baseline subtraction".

* `BaseToRange 2 3 4` _baseline subtracts the second column to minutes 3-4_
* `cjfloop 1 -1 "BaseToRange # 3 4";` _baseline subtracts every column to minutes 3-4_

## CJFLoop
`cjfloop [column first] [column last] "commands to run"`

Run a command on a range of columns on the selected worksheet. The number sign (#) in the "commands to run" string is replaced by the column number. If the last colun is "-1", run the command on every column until the end.

**Examples:**
* `cjfloop 3 6 "BaseToRange # 3 4";` _runs BaseToRange on columns 3, 4, 5, and 6_
* `cjfloop 1 -1 "BaseToRange # 3 4";` _runs BaseToRange on every column from 1 to the end_

## Hline
`hline [value on the vertical axis]`

Draw a horizontal line at a given point on the vertical axis

## Vline
`vline [value on the horizontal axis]`

Draw a vertical line at a given point on the horizontal axis

## ExtractSweeps
`ExtractSweeps`, `ExtractSweeps [first sweep] [last sweep]`

Runs `extractData` on multiple sweeps. If the first and last sweeps are both unspecificed, this will get last 10 sweeps in file (orevery sweep if fewer than 10 sweeps exist). This prevents the user from inadvertendy extracting hundreds of sweeps.

_Note: It is generally not a good idea to store tons of extracted data in an OPJ, espeically without decimation._

## AddTag
`addtag [match] [addition]`

When run with a workbook selected, it finds any sheet with `match` in its name and appends `addition` to its name. You could match `_` so the command works on all sheets, or you could specifically match just `_MT`.
Also see `ChangeTags` and `modifyTags`.

**Examples:**
* `addtag _MT .aged;` _turns `1234_123_MT` into `1234_123_MT.aged`. Run a second time it becomes `1234_123_MT.aged.aged`_

## ChangeTags
`changetags [search] [replace]`

When run with a workbook selected, it performs a search/replace on the tail end of every sheet name in the workbook.
Also see `AddTag` and `modifyTags`.

**Examples:**
* `changetags _MT _MT.aged;` _turns `1234_123_MT` into `1234_123_MT.aged`_
* `changetags _MT.aged _MT.young;` _turns `1234_123_MT.aged` into `1234_123_MT.young`_

## modifyTags
`modifyTags`, `modifyTags [group]`

This command changes modifies the output tags in the global settings dialog without ever exposing the dialog to users. In contrast with commands like `AddTag` and `ChangeTags` which modify _existing_ sheet names, this command configures how _new_ sheets will be named when they are created. The "tag" (the second half of a sheet name separated from the base name by a period) is set with this command, or removed if no argument is given.

**Examples:**
* `modifyTags aged;` _turns `_MT` into `_MT.aged` (and `_eStats.aged`, `_mStats.aged`, etc.)_
* `modifyTags;` _removes all tags from output sheet names, reverting to `_MT`, `_eStats`, etc._

## getGroups
`getGroups [column] [sheets matching] [output sheet]`

This command is identical to `getcols` except that if there are output sheets with group tags (i.e., `_MT.aged`) it will separately run getcols on each group.

**Examples:**
* `getgroups 1 _mStats mean.S` _runs getcols 1 using `_mStats.young` and `_mStats.aged` as search strings_

## NaNum_to_zero
`nanum_to_Zero`

Replace all `--` cells in the selected worksheet with the number `0`. I use this to correct instananeous frequency for gain functions. When no APs are detected (frequency should be 0 instead of NANUM)

## UNKNOWN
This is a list of unknown commands that could benefit from documentation:
* plotTags
* testTag
* clearTags
* normTo
* CJFCheckLicense
* NormToRange
* normToVal
* numbers
* letters
* aligncols
* collectcols
* getxy
* markzero
* selectevery
* runonsheets
* saveascsv
* sortsheets
* setdata
* setlayer
* addplot
* removeplot
* setevoked
* scaletomarks
* autox, autoy, autoxy
* extractdata
* showlocalmaxima
* pave
* plotave
* getstats
* abfbrowse
* scale
* cscale
* inch
* cent
* csize
* atop
* aleft
* setleft, settop, setpos, setsize
* rave, raved, pRave
* setx, sety
* writecolumn
* rstats, vstats
* CPH, CPHprep
* mergecols
