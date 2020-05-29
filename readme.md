#abstract
This generator copy all `package<hash>/lib/pkgconfig/*.pc` to install destination's pkgconfig subdir. Then replace all the prefix path with current package folder.

In cmake we can just set the PKG_CONFIG_PATH/LIBDIR to the `<install path>/pkgconfig`. Then we can use the normal pkg-config based find_package recipes to find all the components.

There is no need to use this generator if the conan package is build from source. Just directly use cmake_paths, the find_package should be able to find the *.pc file in package folder.

#how to use?
1. export the recipe
`conan export . <user>/<channel>`

2. add it to conanfile.txt requires and generators:
```
[requires]
PcFixGen/0.1@<user>/<channel>
[generators]
PcfixGenerator
```