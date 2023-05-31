# QTH Locator Functions
Python functions for converting decimal coordinates to QTH locator and backwards.

## Latitude And Longitude
```
   		         Latitude
                    ^
                    |
               +90° +
                    |
                    |
                    |
                    |              Longitude
   -----+-----------+-----------+----->
      -180°         |         +180°
                    |
                    |
                    |
               -90° +
                    |
                    |
```

## QTH Locator Format

![QTH locator format](https://raw.githubusercontent.com/4x5dm/qth_locator_functions/master/images/qth_locator_format.png)

The Earth's surface is divided into 18x18 fields. Each field is 20°x10° (Lon x Lat). Filed numbers are encoded by first two letters of QTH locator.

Each field is divided into 10x10. Each square is 2°x1°. Square numbers are encoded by first digits pair.

Each square is divided into 24x24 subsquares. Each subsquare is 5'x2.5'. Square is encoded by second two letters of the locator.

Each square is divided into 10x10 extended squares. Each extended square is 0.5'x0.25'. Extended square is encoded by the last two digits of the locator.

```
World (18x18 fields):
           -180° to +180°
        +-----------------+
   +90° |                 |
    to  |      18x18      |
   -90° |      fields     |
        |                 |
        +-----------------+

	   
Fields (10x10 squares):
               20°
        +-----------------+
        |                 |
    10° |      10x10      |
        |     squares     |
        |                 |
        +-----------------+

	   
Squares (10x10 subsquares):
                2°
        +-----------------+
        |                 |
     1° |      24x24      |
        |    subsquares   |
        |                 |
        +-----------------+


Subsquares (10x10 extended squares):
                5'
        +-----------------+
        |                 |
     1' |      10x10      |
        |   ext. squares  |
        |                 |
        +-----------------+


Extended squares:
               0.5'
        +-----------------+
        |                 |
  0.25' |                 |
        |                 |
        |                 |
        +-----------------+
```

## QTH Locator Example

``` KM72jb18 ```

``` K ``` - encodes the 10-th field of longitude (counting from 0),

``` M ``` - encodes the 12-th field of latitude (counting from 0),

``` 7 ``` - encodes the 7-th square of longitude (counting from 0),

``` 2 ``` - encodes the second square of latitude (counting from 0),

``` j ``` - encodes the 9-th subsquare of longitude (counting from 0),

``` b ``` - encodes the first subsquare of latitude (counting from 0),

``` 1 ``` - encodes the first extended square of longitude (counting from 0),

``` 8 ``` - encodes the 8-th extended square of latitude (counting from 0),

It will be translated to coordinates in the following way.

Longitude: ``` -180° + 20°*10 + 2°*7 + 5'*9 + 0.5'*1 = 34°45.5' = 34.75833 ```

Latitude: ``` -90° + 10°*12 + 1°*2 + 2.5'*1 + 0.25'*8 = 32°4.5' = 32.075 ```

## Functions

Module ```qth_locator.py``` contains two functions.

1. ```square_to_location(qth_locator)```

Converts QTH locator to latitude and longitude in decimal format.

Gets QTH locator as string.

Returns Tuple containing latitude and longitude as floats.

2. ```location_to_square(lat, lon)```

Converts latitude and longitude in decimal format to QTH locator.

Gets latitude and longitude as floats or integers.

Returns QTH locator as string.

## Links
1. http://www.jonit.com/fieldlist/maidenhead.htm
2. https://en.wikipedia.org/wiki/Maidenhead_Locator_System
3. http://qthlocator.free.fr/index.php
4. http://www.egloff.eu/googlemap_v3/carto.php

## Questions? Suggestions?
You are more than welcome to contact me with any questions, suggestions or propositions regarding this project. You can:

1. Visit [my QRZ.COM page](https://www.qrz.com/db/4X1MD)
2. Visit [my Facebook profile](https://www.facebook.com/Dima.Meln)
3. Write me an email to iosaaris =at= gmail dot com

## How to Support or Say Thanks

If you like this project, or found here some useful information and want to say thanks, or encourage me to do more, you can buy me a coffee!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Q5Q4ITR7J)

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/4x1md)

You can aslo make a donation with PayPal:

[!["Donate with PayPal"](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate/?hosted_button_id=NZZWZFH5ZBCCU)

---

**73 de 4X1MD**
