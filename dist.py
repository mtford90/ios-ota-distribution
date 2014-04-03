import plistlib
import config
import os

from optparse import OptionParser
from mail import BaseEmail
from s3_interface import S3Interface


class OTADistribution(object):

    s3i = S3Interface(access_key=config.AWS_ACCESS_KEY_ID,
                      secret_key=config.AWS_SECRET_ACCESS_KEY,
                      bucket_name=config.AWS_STORAGE_BUCKET_NAME)

    default_release_notes = '<ul><li>Bug fixes & stability</li></ul>'
    send_address = 'team@mosayc.co.uk'

    def __init__(self, ipa_file_path, version, release_notes_file=None):
        super(OTADistribution, self).__init__()
        self.version = version
        self.release_notes_file = release_notes_file
        self.ipa_file_path = ipa_file_path

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
                                   itms_url=itms_url)
        version = 'Mosayc ' + self.version
        email = BaseEmail(api_key=config.MANDRILL_API_KEY)
        email.send(from_email=self.send_address,
                   from_name='Mosayc Team',
                   to_emails=config.TESTERS,
                   html=html,
                   subject=version)
        if not email.success:
            print 'Email failed: %s' % email.result

    def distribute(self):
        release_notes_data = None
        if self.release_notes_file:
            with open(self.release_notes_file) as f:
                release_notes_data = f.read()
        ipa_file_name = 'mosayc.%s.ipa' % self.version
        ipa_url = self._save_file(location=self.ipa_file_path, name=ipa_file_name)
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


def _exec(cmd):
    print 'Executing ' + cmd
    return os.system(cmd)


def _build(working_dir):
    cmd = "xcodebuild " \
          "-workspace {workspace} " \
          "-scheme {scheme} " \
          "-configuration '{config}' " \
          "build " \
          "-sdk {sdk} " \
          "CONFIGURATION_BUILD_DIR='{absolute_path}'"
    sdk = 'iphoneos'
    configuration = 'Release'
    scheme = 'Mosayc'
    workspace = 'Mosayc.xcworkspace'
    absolute_path = os.path.abspath(working_dir + '/build')
    cmd = cmd.format(absolute_path=absolute_path,
                     sdk=sdk,
                     config=configuration,
                     scheme=scheme,
                     workspace=workspace)
    return _exec(cmd)


def _ipa():
    cmd = "/usr/bin/xcrun " \
          "-sdk {sdk} " \
          "PackageApplication " \
          "-v {build_dir}/Mosayc.app " \
          "-o {build_history_dir}/Mosayc.ipa " \
          "--sign '{signature}' " \
          "--embed '{provisioning_profile}'"
    build_dir = '/Users/mtford/Playground/mosayc/Mosayc/build'
    sdk = 'iphoneos'
    signature = 'iPhone Distribution: Mosayc Ltd. (L82J588522)'
    build_history_dir = '/Users/mtford/Playground/mosayc/Mosayc/buildHistory'
    profiles_dir = '/Users/mtford/Library/MobileDevice/Provisioning Profiles'
    provisioning_profile = '%s/E54EBED1-4DE1-4A79-A7B7-60A9C45882EA.mobileprovision' % profiles_dir
    cmd = cmd.format(build_dir=build_dir,
                     sdk=sdk,
                     signature=signature,
                     build_history_dir=build_history_dir,
                     provisioning_profile=provisioning_profile)
    return _exec(cmd)


def main():
    parser = configure_options()
    (options, args) = parser.parse_args()
    if not options.version:
        parser.error('No version passed')
    # if not len(args):
    #     parser.error('Need to pass directory where Mosayc.xcworkspace resides')
    working_dir = '/Users/mtford/Playground/mosayc/Mosayc/'
    os.chdir(working_dir)
    build_status = _build(working_dir)
    if not build_status == 0:
        print 'Build failed'
        exit(build_status)
    ipa_status = _ipa()
    if not ipa_status == 0:
        print 'Archive failed'
        exit(ipa_status)
    ipa_file = '/Users/mtford/Playground/mosayc/Mosayc/buildHistory/Mosayc.ipa'
    ota = OTADistribution(ipa_file_path=ipa_file,
                          version=options.version,
                          release_notes_file=options.release_notes_file_path)
    ota.distribute()


if __name__ == '__main__':
    main()
