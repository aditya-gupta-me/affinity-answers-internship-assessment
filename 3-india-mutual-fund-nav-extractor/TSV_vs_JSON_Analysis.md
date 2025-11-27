# TSV vs JSON: Format Selection Analysis

## Question

_"Ever wondered if this data should not be stored in JSON?"_

## Answer: What my intuition says, TSV is the Right Choice for This Use Case

### Why TSV?

**1. Data Structure**: Flat, tabular data (2 columns) - exactly what TSV is designed for

**2. Size**: With 8,500+ schemes, TSV is ~50% smaller than JSON (~500KB vs ~750KB)

**3. Compatibility**: Direct import to Excel, Google Sheets, databases, pandas - no parsing needed

**4. Speed**: Simple line-by-line reading, no JSON parser required

### When JSON Makes Sense

- **Complex/Nested data**: Multiple levels, arrays, objects
- **API integration**: Web applications expect JSON
- **Type preservation**: Distinguishing numbers from strings matters

### My Approach

Support both formats to cover different use cases:

```bash
./extract_amfi_nav.sh --format=tsv   # Default - data analysis
./extract_amfi_nav.sh --format=json  # For web/API use
```

### Conclusion

For simple, high-volume tabular data like AMFI NAV listings, **TSV is optimal**. JSON would add unnecessary overhead. However, offering both formats demonstrates understanding of each format's strengths and provides flexibility for different use cases.
