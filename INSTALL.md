# Installation Guide

This guide will help you set up the India Internal Migration Mapping application on your local machine.

## Prerequisites

- Python 3.12 or higher
- uv package manager
- Git (for cloning the repository)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/amitportal/india_internal_migration_mapping.git
cd india_internal_migration_mapping
```

### 2. Install uv (if not already installed)

If you don't have uv installed, you can install it using pip:

```bash
pip install uv
```

Or using other methods from the [uv documentation](https://github.com/astral-sh/uv).

### 3. Install Dependencies

Use uv to create a virtual environment and install all dependencies:

```bash
uv sync
```

This will create a virtual environment and install all required packages as specified in the `pyproject.toml` file.

### 4. Prepare Data Files

The application requires two data files to be present in the root directory:

1. `IND_5yrs_InternalMigFlows_2010.csv` - Migration flow data
   - Should contain columns: ISO, NODEJ, NODEI, LONFR, LATFR, LONTO, LATTO, PrdMIG

2. `india_states.geojson` - Indian state boundaries
   - Should contain features with properties: state, country, and geometry

### 5. Run the Application

Start the Flask application:

```bash
uv run python app.py
```

### 6. Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage Tips

- The application will automatically fit to India's boundaries on startup
- Zoom in/out to see different levels of geographic detail
- Click on states to see detailed migration information
- Click on migration flows to highlight all related flows between states
- Press ESC to deselect and return to hover mode
- Use the controls panel to filter different types of migration flows

## Troubleshooting

### Common Issues

1. **Module not found errors**: Make sure you're running the application using `uv run python app.py` and not regular `python`

2. **Missing data files**: Ensure both required CSV and GeoJSON files are in the root directory

3. **Performance issues**: This application processes significant geospatial data. Performance may vary based on your system specifications

### Required File Formats

**CSV Format Example:**
```
ISO,NODEJ,NODEI,LONFR,LATFR,LONTO,LATTO,PrdMIG
IND,1,2,77.23308096,31.92721256,76.61263777,33.75942968,16913.78344
```

**GeoJSON Format Example:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "state": "Delhi",
        "country": "India"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [...]
      }
    }
  ]
}
```

## Development Setup

If you want to contribute to the project:

1. Fork the repository
2. Clone your fork
3. Create a virtual environment: `uv venv`
4. Activate it: `source .venv/bin/activate` (Linux/Mac) or `source .venv/Scripts/activate` (Windows)
5. Install dependencies: `uv pip install -e .`
6. Make your changes
7. Test the application: `uv run python app.py`

## Updating Dependencies

If you need to update dependencies:

1. Modify the `pyproject.toml` file as needed
2. Run: `uv sync --upgrade`
3. Commit the updated `uv.lock` file

## Next Steps

After successful installation:
- Explore the migration patterns on the map
- Try different filter options
- Test the selection functionality
- Review the detailed state information in the side panel