# This is based loosely on Softthinker's java code found here
# http://www.softhinker.com/in-the-news/iosmdmvendorcsrsigning
# fuck java

import argparse
from plistlib import writePlistToString
import os
import subprocess
from base64 import b64encode
import sys
import urllib2

def p(s):
	sys.stdout.write(s)
	sys.stdout.flush()

def mdm_vendor_sign():
	"""
	This utility will create a properly encoded certifiate signing request
	that you can upload to identity.apple.com/pushcert
	"""

	parser = argparse.ArgumentParser(description=mdm_vendor_sign.__doc__)
	parser.add_argument('--key', help='Private key', required=True)
	parser.add_argument('--csr', help='Certificate signing request', required=True)
	parser.add_argument('--mdm', help='MDM vendor certificate', required=True)
	parser.add_argument('--out', help='Output filename', required=False)


	cli_args = vars(parser.parse_args())

	# Verify CSR
	# openssl req -text -noout -verify -in CSR.csr
	p('Verifying %s ... ' % cli_args['csr'])
	csr_file = open(cli_args['csr']).read()
	args = ['openssl', 'req', '-noout', '-verify' ]
	command = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
	output, error = command.communicate(input = csr_file)	
	if output.rstrip().split('\n')[0] == 'verify OK':
		p('OK\n')
	else:
		p('FAILED\n')
		return


	# Verify private key
	# openssl rsa -in privateKey.key -check
	p('Verifying %s ... ' % cli_args['key'])
	key_file = open(cli_args['key']).read()
	args = ['openssl', 'rsa', '-check', '-noout' ]
	command = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
	output, error = command.communicate(input = key_file)	
	if output.rstrip().split('\n')[0] == 'RSA key ok':
		p('OK\n')
	else:
		p('FAILED\n\n')
		print """If you don't have the plain private key already, you need
to extract it from the pkcs12 file...

First convert to PEM
openssl pkcs12 -in filename.p12 -nocerts -out key.pem

Then export the certificate file from the pfx file
openssl pkcs12 -in filename.pfx -clcerts -nokeys -out cert.pem

Lastly Remove the passphrase from the private key
openssl rsa -in key.pem -out the_private_key.key
"""
		return


	# Verify MDM vendor certificate
	# openssl x509 -noout -in mdm.cer -inform DER
	p('Verifying %s ... ' % cli_args['mdm'])
	mdm_cert_file = open(cli_args['mdm'],'rb').read()  # Binary read
	args = ['openssl', 'x509', '-noout', '-inform', 'DER' ]
	command = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
	output, error = command.communicate(input = mdm_cert_file)	
	if len(output) == 0:
		p('OK\n')
	else:
		p('FAILED\n')
		return


	# Convert CSR to DER format
	# openssl req -inform pem -outform der -in customer.csr -out customer.der
	p('Converting %s to DER format... ' % cli_args['csr'])
	args = ['openssl', 'req', '-inform', 'pem', '-outform', 'der' ]
	command = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
	output, error = command.communicate(input = csr_file)	
	if error:
		p('FAILED\n')
		return
	p('OK\n')
	csr_der = output
	csr_b64 = b64encode(csr_der)


	# Sign the CSR with the private key 
	# openssl sha1 -sign private_key.key -out signed_output.rsa data_to_sign.txt
	p('Signing CSR with private key... ')
	args = ['openssl', 'sha1', '-sign', cli_args['key'] ]
	command = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
	output, error = command.communicate(input = csr_der)
	if error:
		p('FAILED\n')
		return
	p('OK\n')
	signature_bytes = output
	signature = b64encode(signature_bytes)


	def cer_to_pem(cer_data):
		# openssl x509 -inform der -in mdm.cer -out mdm.pem
		# -in and -out flags are handled by STDIN and STDOUT
		args = ['openssl', 'x509', '-inform', 'der' ]
		command = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
		output, error = command.communicate(input = cer_data)
		if error:
			p('Error converting from cer to pem: %s' % error)
		return output


	# TODO : Probably should verify these too

	p('Downloading WWDR intermediate certificate...')
	intermediate_cer = urllib2.urlopen('https://developer.apple.com/certificationauthority/AppleWWDRCA.cer').read()
	p(' converting to pem...')
	intermediate_pem = cer_to_pem(intermediate_cer)
	p('OK\n')

	p('Downloading Apple Root Certificate...')
	root_cer = urllib2.urlopen('http://www.apple.com/appleca/AppleIncRootCertificate.cer').read()
	p(' converting to pem...')
	root_pem = cer_to_pem(root_cer)
	p('OK\n')

	mdm_pem = cer_to_pem(mdm_cert_file)

	p('Finishing...')
	plist_dict = dict(
	    PushCertRequestCSR = csr_b64,
	    PushCertCertificateChain = mdm_pem + intermediate_pem + root_pem,
	    PushCertSignature = signature
	)
	plist_xml = writePlistToString(plist_dict)
	plist_b64 = b64encode(plist_xml)

	output_filename =  cli_args['out'] if  cli_args['out'] else 'plist_encoded'
	write_path = os.path.join(os.getcwd(), output_filename)
	output = open(write_path, 'wb')
	output.write(plist_b64)
	output.close()
	p('DONE\n\nGo upload file \'%s\' to identity.apple.com/pushcert !\n' % output_filename)



if __name__=="__main__":
	mdm_vendor_sign()
