

import setuptools 

with open("README.md", "r", encoding="utf-8") as fh: 
   long_description = fh.read()
 
setuptools.setup(
   name = "music_event_app",
   version = "0.0.1",
   author = "Mohamed njah",
   author_email = "mnjah@stud.macromedia.de",
   description = "A small example package",
   long_description = long_description,
   long_description_content_type = "text/markdown",
   url = "https://github.com/pypa/mohamednjahsamplepackage",
   project_urls = {
      "Bug Tracker": "https://github.com/pypa/mohamednjahsamplepackage/issues",
   },
   classifiers = [
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
   ],
   package_dir = {"": "event_manager"},
   packages = setuptools.find_packages(where = "event_manager"),
   python_requires = ">=3.6", 
) 
 