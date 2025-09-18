
# synapse-quantum

Example Synapse package demonstrating package structure and features.

## Installation

```bash
syn-pkg install ./synapse-quantum
```

## Usage

```synapse
import synapse-quantum

// Basic usage
synapse-quantum.hello()

// Get version
version = synapse-quantum.version()

// Scientific calculations
data = [1, 2, 3, 4, 5]
results = synapse-quantum.calculate(data)
print("Mean:", results.mean)
print("Std:", results.std)
```

## API Reference

### `hello()`
Prints a greeting message.

### `version()`
Returns the package version.

### `calculate(data)`
Performs statistical calculations on data.
- **Parameters**: `data` - Array of numeric values
- **Returns**: Object with `mean` and `std` properties

## License

MIT
