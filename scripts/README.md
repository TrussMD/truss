# Scripts

The schemas and the conformance cases are generated. Edit these scripts, not the generated files, then run both:

```sh
node scripts/gen-schemas.mjs        # writes spec/schemas/
python scripts/gen-conformance.py   # writes spec/conformance/
```

CI runs both and fails if the committed files differ. Neither script needs a network connection or any package beyond Node and Python's standard libraries.
