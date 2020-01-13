#!/usr/bin/python
#
# Process the Installation Guide to a format suitable for use as built-in-help in Anaconda
import os
import shutil
import glob
import subprocess
# we are using lxml as unlike in the Python built-in ElementTree elements
# in the lxml tree know their parents - this is handy when removing the figure tags
from lxml import etree as ET


PLACEHOLDERS = ["RHEL7PlaceholderWithLinks.html", "RHEL7Placeholder.html"]
INPUT_FOLDER = "en-US"
OUTPUT_FOLDER_RHEL = "anaconda_help_content/rhel/en-US"
OUTPUT_FOLDER_RHV = "anaconda_help_content/rhv/en-US"

DEFAULT_PRODUCT_NAME = "Red Hat Enterprise Linux"
RHV_PRODUCT_NAME = "Red Hat Virtualization"

MAIN_ENTITY_FILE = "Installation_Guide.ent"

# list of the XML help content & supporting files Anaconda currently cares about
ANACONDA_HELP_FILES = [
	"Graphical_Installation-x86.xml",
	"WelcomeSpoke-x86.xml",
	"SummaryHub-x86.xml",
	"DateTimeSpoke-x86.xml",
	"LangSupportSpoke-x86.xml",
	"KeyboardSpoke-x86.xml",
	"SecurityPolicySpoke-x86.xml",
	"SourceSpoke-x86.xml",
	"NetworkSpoke-x86.xml",
	"SoftwareSpoke-x86.xml",
	"StorageSpoke-x86.xml",
	"CustomSpoke-x86.xml",
	"FilterSpoke-x86.xml",
	"KdumpSpoke-x86.xml",
	"Write_changes_to_disk_x86.xml",
	"ProgressHub-x86.xml",
	"PasswordSpoke-x86.xml",
	"UserSpoke-x86.xml",
	"Complete-x86.xml",
	"Graphical_Installation-ppc.xml",
	"WelcomeSpoke-ppc64.xml",
	"SummaryHub-ppc64.xml",
	"DateTimeSpoke-ppc64.xml",
	"LangSupportSpoke-ppc64.xml",
	"KeyboardSpoke-ppc64.xml",
	"SecurityPolicySpoke-ppc64.xml",
	"SourceSpoke-ppc64.xml",
	"NetworkSpoke-ppc64.xml",
	"SoftwareSpoke-ppc64.xml",
	"StorageSpoke-ppc64.xml",
	"CustomSpoke-ppc64.xml",
	"FilterSpoke-ppc64.xml",
	"KdumpSpoke-ppc64.xml",
	"Write_changes_to_disk_ppc.xml",
	"ProgressHub-ppc64.xml",
	"PasswordSpoke-ppc64.xml",
	"UserSpoke-ppc64.xml",
	"Complete-ppc.xml",
	"Graphical_Installation-s390.xml",
	"WelcomeSpoke-s390.xml",
	"SummaryHub-s390.xml",
	"DateTimeSpoke-s390.xml",
	"LangSupportSpoke-s390.xml",
	"KeyboardSpoke-s390.xml",
	"SecurityPolicySpoke-s390.xml",
	"SourceSpoke-s390.xml",
	"NetworkSpoke-s390.xml",
	"SoftwareSpoke-s390.xml",
	"StorageSpoke-s390.xml",
	"CustomSpoke-s390.xml",
	"FilterSpoke-s390.xml",
	"KdumpSpoke-s390.xml",
	"Write_changes_to_disk_s390.xml",
	"ProgressHub-s390.xml",
	"PasswordSpoke-s390.xml",
	"UserSpoke-s390.xml",
	"Complete-s390.xml",
	"InitialSetupHub-common.xml",
	"SubscriptionManagerSpoke-common.xml",
	"InitialSetup-text.xml",
    "Installation_Guide.ent"
]

def run_xmllint(output_folder):
    for path in glob.glob(os.path.join(output_folder, "*.xml")):
        try:
            temp_file_path = "%s.temp" % path
            # xmllint outputs to stdout, so we catch the output to a temporary
            # file and then overwrite the original with the temporary file once
            # xmllint is done
            temp_file = open(temp_file_path, "w")
            subprocess.check_call(["xmllint", "--noent", path], stdout=temp_file)
            temp_file.close()
            shutil.move(temp_file_path, path)
        except subprocess.CalledProcessError:
            print("WARNING: running xmllint on %s failed" % path)

# does the input folder exist ?
if not os.path.isdir(INPUT_FOLDER):
    print("ERROR: input folder does not exists")
    exit(1)

def generate_help_content(output_folder, product_name=None):
    # if product name is not set we expect to generate
    # generic RHEL help content
    if product_name:
        print("Generating help content files for %s" % product_name)
    else:
        print("Generating help content files for RHEL")
    # make sure that the output folder is empty
    if os.path.exists(output_folder):
        # if it already exists, delete it
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    print("copying relevant help content files")
    for file_name in ANACONDA_HELP_FILES:
        origin = os.path.join(INPUT_FOLDER, file_name)
        destination = os.path.join(output_folder, file_name)
        if not os.path.isfile(origin):
            print("WARNING: required file %s is missing" % origin)
        shutil.copy(origin, destination)

    print("removing non breakable spaces")
    for path in glob.glob(os.path.join(output_folder, "*.ent")):
        os.system("sed 's/&nbsp;/ /g' -i %s %s" % (path, path))
    for path in glob.glob(os.path.join(output_folder, "*.xml")):
        os.system("sed 's/&nbsp;/ /g' -i %s %s" % (path, path))

    # change the product name if required
    if product_name is not None:
        print("using non-default product name: %s" % product_name)
        entity_file_path = os.path.join(output_folder, MAIN_ENTITY_FILE)
        os.system("sed 's/%s/%s/g' -i %s %s" % (DEFAULT_PRODUCT_NAME,
                                                product_name,
                                                entity_file_path,
                                                entity_file_path))

    # run xmllint to resolve entities
    print("running xmllint to resolve entities")
    run_xmllint(output_folder)

    print("loading all XML files")

    xml_files = {}
    known_ids = {}

    for path in glob.glob(os.path.join(output_folder, "*.xml")):
        print("loading: %s" % path)
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            # find all elements that have an id attribute
            for element in root.iter():
                id = element.attrib.get("id")
                # the element has an id attribute
                if id:
                    title = element.find('title')
                    if hasattr(title, "text"):
                        # store the tile text and filename under the id
                        filename = os.path.split(path)[1]
                        known_ids[id] = (filename, title.text)
                    else:
                        # some title elements might not have any text property
                        print("WARNING: id %s in %s has no title text" % (id, path))

            xml_files[path] = tree
        except ET.ParseError as err:
            print("WARNING: parsing failed:\n%s" % err)

    print("%d XML files loaded" % len(xml_files))
    print("%d ids found" % len(known_ids))

    # remove pictures/figures
    removed_figures = 0
    removed_remarks = 0
    rewritten_links = 0
    outside_links = 0
    print("removing figure & remark tags, rewriting links")
    for path, tree in xml_files.items():
        root = tree.getroot()

        for figure in root.findall('.//figure'):
            parent = figure.getparent()
            parent.remove(figure)
            removed_figures += 1

        for remark in root.findall('.//remark'):
            parent = remark.getparent()
            parent.remove(remark)
            removed_remarks += 1

        # rewrite all links to a format digestible by Yelp
        for xref in root.findall('.//xref'):
            link_target = xref.attrib.get('linkend')
            if link_target:
                if link_target in known_ids:
                    filename, title = known_ids[link_target]
                    new_element = ET.Element("ulink")
                    new_element.attrib["url"] = filename
                    new_element.text = title
                    new_element.tail = xref.tail
                    # replace the old link element with the new one
                    xref.getparent().replace(xref, new_element)
                else:
                    # this link points outside of the help files currently
                    # used by Anaconda, so replace it with "find it somewhere else"
                    # template
                    print("INFO: outside link, id: %s in %s" % (link_target, path))
                    # lxml doesn't seem to be able to replace an element with a string,
                    # so we will just clear the element and replace it with the templates
                    # in a later sed pas :P
                    tail = xref.tail
                    # clear() removes the tail, which is in this case pretty much unrelated
                    # to the element, so we need to make sure to save & restore it
                    xref.clear()
                    xref.tail = tail
                    outside_links += 1
                rewritten_links += 1
            else:
                print("WARNING: %s has a xref link with missing linkend" % path)

    print("%d figures and %d remarks have been removed" % (removed_figures, removed_remarks))
    print("%d links have been rewritten, %d were outside links" % (rewritten_links, outside_links))

    # write the modified XMLs to disk
    print("saving modified XMLs to storage")
    for path, tree in xml_files.items():
        tree.write(path)

    # replace the outside links here with sed as lxml is not able to do that for us
    print("removing obsolete <xref/> tags")
    template = "the full <citetitle>\&PRODUCT\; Installation Guide<\/citetitle>, available at \&IGURL\;"
    for path in glob.glob(os.path.join(output_folder, "*.xml")):
        os.system("sed 's/<xref\/>/%s/g' -i %s %s" % (template, path, path))

    # resolve any newly added entities
    print("running xmllint to resolve any newly added entities")
    run_xmllint(output_folder)

    # remove the entity file, it is no longer needed
    print("removing the entity file")
    os.remove(os.path.join(output_folder, "Installation_Guide.ent"))

    print("adding placeholders:")
    for placeholder in PLACEHOLDERS:
        shutil.copy(os.path.join(INPUT_FOLDER, placeholder), output_folder)
        print(placeholder)

print("creating generic RHEL help content")
generate_help_content(output_folder=OUTPUT_FOLDER_RHEL)
print("creating RHV help content")
generate_help_content(output_folder=OUTPUT_FOLDER_RHV, product_name=RHV_PRODUCT_NAME)
print("done!")
exit(0)
