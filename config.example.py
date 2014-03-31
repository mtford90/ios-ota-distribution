__author__ = 'mtford'

# Manifest file settings
MANIFEST_FILE_NAME = 'manifest.{version}.plist'
PROJECT_NAME = 'Mosayc'
BUNDLE_IDENTIFIER = 'com.yourcompany.%s' % PROJECT_NAME
BUNDLE_NAME = '?'
TARGET_SDK = 'iphoneos'

TESTERS = ['blah@gmail.com']

APP_NAME = 'Mosayc'

EMAIL = '<html> \
           <body> \
               <p>Hello Tester!</p> \
               <p>A new version has been released. Please click \
               <a href="{manifest_url}">here</a> to install on your device.</p>\
               <p>Below is a summary of updates and features that have been added since the last version:</p> \
               <p>{itms_url}</p> \
           </body> \
       </html>'

AWS_ACCESS_KEY_ID = '?'
AWS_SECRET_ACCESS_KEY = '?'
AWS_STORAGE_BUCKET_NAME = '?'