# mdmvendorsign
=============

Create a certificate signing request as a "vendor" of Apple's MDM push notification service

This script produces the special encoded plist that is uplaoded to the [Apple Push Certificate Portal] (https://identity.apple.com/pushcert/) for creating certificates to work with Apple's [Mobile Device Management](http://www.apple.com/iphone/business/it-center/deployment-mdm.html) (MDM) system.

Usually, this certificate is obtained by uploading a certificate request (CSR) to your MDM vendor who then signs the certificate using their MDM Signing Certificate. If you are part of the iOS Developer Enterprise Program, you can request a vendor certificate and do this youself.

=============

## Usage

Run it something like this 
```
python mdm_vendor_sign.py  --csr CSR.csr --key disconnect.key --mdm mdm.cer
```

Use `-h` to list the options, as such


```
$ python mdm_vendor_sign.py -h
usage: mdm_vendor_sign.py [-h] --key KEY --csr CSR --mdm MDM [--out OUT]

This utility will create a properly encoded certifiate signing request that
you can upload to identity.apple.com/pushcert

optional arguments:
  -h, --help  show this help message and exit
  --key KEY   Private key
  --csr CSR   Certificate signing request
  --mdm MDM   MDM vendor certificate
  --out OUT   Output filename
```

It has a few dependencies that you might need to `pip install`...
