## Todo

* [ ] :test_tube: New shortcut - `[z]` Break line automatically if text is wider than console screen, when using timestamp. (default is `ON`)
* [ ] :test_tube: Input mode don't add extra line
- [ ] Use temporary text file to improve rendering stability on no-latency mode.

## 0.7.0 (alpha)

2022/04/08 **First GitHub release!**

* New shortcut - `[d]` Decode mode  utf-8 `default`
  * `'0','u','utf'` Utf-8  `default`
  * `'1','n','uni'` Unicode
  * `'2','h','hex'` Hexadecimal
  * `'3','d','dec'` Decimal (bytes)
  * `-ln` New line character will render a new line (hex and decimal mode)
* Fixed extended ascii font don''t matches Windows' character table.
* Shortcut changed - `[o]` Open connection manually. (default)
  * `[O]` Open connection and reconnect.

## 0.6.0 (alpha)

2022/02/13

* New shortcut - `[l]` Serial visualization with no latency (default is `ON`).
* Fix footer not updating when input mode and no serial activity
* Serial text with no `new line`  (`\n`) will display the folowing one on the side.
* All ASCII characters are displayed with printable characters, including: `NULL`, `Vertical Tab`, `Form Feed`, `DEL` and `NBSP`.
  * New shortcut - `[s]` Choose serial font:
    * `'0','s','symbol'` Symbol  `default`
      * ♢  |☺ |☻ |a   |b   |c    |⌂   |╝    |◖
    * `'1','t','text'` Text
      * ␀   |␁   |␂  |a   |b   |c   |␡   |╝    |◖
    * `'0','a','arduino'` Arduino
      * ▯  |▯ |▯ |a   |b   |c   |⸮    |╝    |⸮
    * Character code for comparison:
      * 0   |1  |2   |97 |98 |99 |127|188|255
  * Unicode and utf combining characters `128-255` are not customizable yet.
* Shortcut changed - `[t]` Timestamp show only milliseconds. (default is `show`)
* Fix links not clickable and doesnt open, unless when input mode or quit.
* Shortcut readded -`[b]` Baud rate menu, see all available baud rates and change it.
* Shortcut readded -`[p]` Port menu, See all available ports and change it.
  * If connection mode is set to `find` it will change to `auto.`
* Fix high cpu usage of terminal
* Readded shortcuts - connection options:
  * `[c]` Close (connection mode = `manual`)
  * `[O]` Open manulaly (connection mode = `manual`)
  * `[o]` Open and reconnect (conection mode = `reconnect`)
  * `[f]` Find and open (connection mode = `find`) (default)
    * Open chosen port or find available ports.
    * Try reconnect again.
* New shortcut - `[h]` Help
* Help information updated:
  * Connection mode info changed to be more legible
  * Info about new and changed commands

## 0.5.0 (alpha)

2022/02/05

* Fix crash when reconnect the last available port
* Fix serial port status doesn't update when gets disconected
* Prevent stale lock serial ports when unneeded
* Fix high cpu usage of the program
* Shortcut changed - `[T][t]` Alternate betwen timestamp formats:
  * Distabled
  * Milliseconds (0.123) `default`
  * Microseconds (0.123456)

## 0.4.0 (alpha)

2022/01/31

* Fix serial port not connecting selected port at start
* Fix program crash on try reading serial in certain conditions.
* Fix all serial ports getting busy randomly.
* Decoding mode changed from ASCII to UTF-8
* New shortcut - `[u]` Show/hide undedable raw characters if decoding fails. (default is `show`)
* Fix input mode footer not showing sometimes.
* "Input message" footer sending empty content is cleared, it doesnt send anything after all.

## 0.3.0 (alpha)

2022/01/21

* Fixed serious bug that crash the program when port is unplugged or changed.
* Temporariry disabled all connection, baudrate and port functions.
* Basically this is the version 0.1.0 improved with some of features, fixes and modifications made in 0.2.0, but only the known stable ones. Slowly other improvements may be added back.

## 0.2.0 (alpha)

2022/01/20

* Baud rate menu: See all available baud rates and change.
* Port menu: See all available ports and change.
* New shortcuts - connection options:
  * `[o]` Open (conection `auto reconnect`)
  * `[c]` Close (connection `manual`)
  * `[m]` Open (connection `manual`)
  * `[f]` Find available port and open (connection `any available`)
* Initialization options (flags)
* Detailed help menu
* Shortcut for quit program changed from  `[c]` to `[q]`
* Status bar shows serial port and baud rate
* Fixed delay in monitor on type commands
* Serial error message removed

## 0.1.0 (alpha)

2022/01/17 **First version**

* Persistent status bar showing serial port and input mode.
* Auto connect available ports.
* Wait serial port be available when disconnected.
* Show/hide timestamp on pressing `t`
