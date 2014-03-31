import plistlib
import config

from optparse import OptionParser
from mail import BaseEmail
from s3_interface import S3Interface


class OTADistribution(object):

    s3i = S3Interface(access_key=config.AWS_ACCESS_KEY_ID,
                      secret_key=config.AWS_SECRET_ACCESS_KEY,
                      bucket_name=config.AWS_STORAGE_BUCKET_NAME)

    default_release_notes = '<ul><li>Bug fixes & stability</li></ul>'
    send_address = 'team@mosayc.co.uk'

    def __init__(self, ipa_file, version, release_notes_file=None):
        super(OTADistribution, self).__init__()
        self.version = version
        self.release_notes_file = release_notes_file
        self.ipa_file = ipa_file

    def _save_file(self, name, location):
        with open(location) as f:
            return self.s3i.write_string(f.read(), name)

    def _construct_itms_url(self, manifest_url):
        return 'itms-services://?action=download-manifest&amp;url=%s' % manifest_url

    def _construct_manifest(self, ipa_url):
        manifest_plist = {
            'items': [{
                'assets': [{
                    'kind': 'software-package',
                    'url': ipa_url,
                }],
                'metadata': {
                    'bundle-identifier': config.BUNDLE_IDENTIFIER,
                    'bundle-version': self.version,
                    'kind': 'software',
                    'title': config.BUNDLE_NAME,
                    'subtitle': config.BUNDLE_NAME
                }
            }]
        }
        manifest_file_name = config.MANIFEST_FILE_NAME.format(version=self.version)
        plistlib.writePlist(manifest_plist, manifest_file_name)
        return self._save_file(manifest_file_name, manifest_file_name)

    def _send_emails(self, itms_url, release_notes_data=None):
        if not release_notes_data:
            release_notes_data = self.default_release_notes
        html = config.EMAIL.format(release_notes_data=release_notes_data,
                                   manifest_url=itms_url)
        version = 'Mosayc ' + self.version
        email = BaseEmail(from_email=self.send_address,
                          to_emails=config.TESTERS,
                          message=html,
                          subject=version)
        email.send()
        if not email.success:
            print 'Email failed: %s' % email.result

    def distribute(self):
        release_notes_data = None
        if self.release_notes_file:
            with open(self.release_notes_file) as f:
                release_notes_data = f.read()
        ipa_file_name = 'mosayc.%s.ipa' % self.version
        ipa_url = self._save_file(location=self.ipa_file, name=ipa_file_name)
        manifest_url = self._construct_manifest(ipa_url)
        itms_url = self._construct_itms_url(manifest_url)
        self._send_emails(itms_url, release_notes_data)


def configure_options():
    parser = OptionParser(usage='usage: %prog [options]')
    parser.add_option("-v", "--version", action="store", type="string",
                      dest="version",
                      help="version of release e.g. 0.12, if new build then sets version. if resend, then sends latest"
                           " build with that version",
                      metavar="VERSION", default=None)
    parser.add_option("-f", "--release-notes-file", action="store", type="string", dest="release_notes_file_path",
                      default=None, help="file path for html file used for release notes", metavar="FILE")
    return parser


def main():
    parser = configure_options()
    (options, args) = parser.parse_args()
    if not options.version:
        parser.error('No version passed')
    ota = OTADistribution(ipa_file=args[0],
                          version=options.version,
                          release_notes_file=options.release_notes_file_path)
    ota.distribute()


if __name__ == '__main__':
    main()
