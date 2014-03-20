# mdmvendorsign
=============

Create a certificate signing request as a "vendor" of Apple's MDM push notification service

This script produces the special encoded plist that is uplaoded to the [Apple Push Certificate Portal] (https://identity.apple.com/pushcert/) for creating certificates to work with Apple's [Mobile Device Management](http://www.apple.com/iphone/business/it-center/deployment-mdm.html) (MDM) system.

Usually, this certificate is obtained by uploading a certificate request (CSR) to your MDM vendor who then signs the certificate using their MDM Signing Certificate. If you are part of the iOS Developer Enterprise Program, you can request a vendor certificate and do this youself.

=============

## Setup

This script is what an _MDM vendor_ would use to sign a user-submitted CSR. That user isn't going to submit their private key to the vendor, obviously.

To get an MDM Vendor Certificate from Apple, you need to create a CSR. You need a private key to create the CSR. That private key is the _Vendor's private key_ (`mdm_vendor_private.key` below). The `--mdm` argument should point to the MDM certificate that Apple has ussed you.

Note that they don't enable the MDM Vendor program by default. The registered Team Agent needs to email devprograms@apple.com and say something like _"I am writing to request a MDM Vendor signing certificate for Acme, Inc. I am listed as the Team Agent for our Enterprise Developer Program account."_

Once they accept your request, you should see the following option when creating a new certificate on the developer site:

![Provisioning Profile Screenshot](https://f.cloud.github.com/assets/92417/960108/51d1bc22-04ab-11e3-840e-d3f12fc62765.png)


This script is essentially a shortcut for a lot of the stuff in this StackOverflow Question: [Apple MDM Vendor CSR Signing](http://stackoverflow.com/questions/8501039/apple-mdm-vendor-csr-signing). For more details on MDM, I recommend reading [this document](http://media.blackhat.com/bh-us-11/Schuetz/BH_US_11_Schuetz_InsideAppleMDM_WP.pdf) by the Intrepidus Group.


## Usage

Run it something like this 
```
python mdm_vendor_sign.py  --csr user_submitted_CSR.csr --key mdm_vendor_private.key --mdm mdm_certifiate_from_apple.cer
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
