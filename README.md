# Manifest File Extractor

This lib allows you to extract files from a manifest file (.far) used on The Sims game and save them to a specified output path.

## Prerequisites

- Python >= 3.10

## Example Usage

```python
# Generate a manifest from a .far file
manifest = create_manifest(far_file_path="path/to/file.far")

# Extract files from the manifest
extract_manifest_files(manifest=manifest, output_path="path/to/output", far_file_path="path/to/file.far")
```

The files will be extracted to the specified far_file_path. Please note that some files have subdirectories in their names, and these subdirectories will be automatically created by default.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvement, please open an issue or submit a pull request.

## License

This code is released under the MIT License.

Feel free to modify and use it according to your needs.

## References

Based on the great content provided by Greg Noel and Peter Gould about the technical aspects of The Sims.

- https://web.archive.org/web/20220410061532/https://simtech.sourceforge.net/tech/far.html