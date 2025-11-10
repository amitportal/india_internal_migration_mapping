# India Internal Migration Mapping

An interactive web application for visualizing internal migration flows across Indian states with dynamic boundary loading and detailed migration analytics.

## Features

- **Interactive Migration Map**: Visualize in-migration (blue), out-migration (red), and net migration (white dashed) flows
- **Dynamic Boundary Loading**: 10 levels of geometric simplification based on zoom level
- **State Selection**: Click on states or flows to highlight related migration patterns
- **Detailed Analytics**: Side panel showing detailed migration data for selected states
- **Filter Controls**: Toggle different flow types and adjust minimum flow thresholds
- **Keyboard Navigation**: Press ESC to deselect and return to hover mode

## Technology Stack

- **Backend**: Flask with Python
- **Frontend**: Leaflet.js, HTML5, CSS3, JavaScript
- **Data Processing**: Pandas, GeoPandas, Shapely
- **Dependencies Management**: uv (Python package manager)

## Installation

### Prerequisites
- Python 3.12+
- uv package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/amitportal/india_internal_migration_mapping.git
cd india_internal_migration_mapping
```

2. Install dependencies using uv:
```bash
uv sync
```

### Required Data Files

The application requires the following data files in the root directory:
- `IND_5yrs_InternalMigFlows_2010.csv` - Migration flow data
- `india_states.geojson` - Indian state boundaries

## Usage

1. Run the application:
```bash
uv run python app.py
```

2. Open your browser and navigate to `http://localhost:5000`

## Data Structure

### Migration Flow CSV
The application expects a CSV file with the following columns:
- `ISO`: Country identifier
- `NODEJ`: Origin node ID
- `NODEI`: Destination node ID
- `LONFR`, `LATFR`: Origin coordinates
- `LONTO`, `LATTO`: Destination coordinates
- `PrdMIG`: Migration volume

### GeoJSON Format
State boundaries should be in GeoJSON format with:
- `state`: State name
- `country`: Country name (should be "India")
- `geometry`: State boundary geometry

## Functionality

### Map Interaction
- **Hover**: Shows state names and highlights related flows (when no selection is active)
- **Click on State**: Highlights all flows to/from that state, shows detailed information
- **Click on Flow**: Highlights all three flow types (in, out, net) between the two states
- **ESC Key**: Deselects current selection and enables hover functionality
- **Zoom**: Dynamically loads boundaries with appropriate detail level

### Flow Types
- **Red Lines**: Out-migration flows (from origin state to destination)
- **Blue Lines**: In-migration flows (to destination state from origin)
- **White Dashed Lines**: Net migration flows (balance between in and out migration)

### Controls
- Toggle flow types (in-migration, out-migration, net migration)
- Adjust minimum flow size with slider
- Reset highlighting functionality

## Architecture

The application follows a client-server architecture:

### Backend (Flask)
- Handles data loading and processing
- Provides API endpoints for:
  - Boundary data with zoom-level appropriate simplification
  - Migration flow data
  - State-specific migration details
  - Overall statistics

### Frontend (Leaflet.js)
- Interactive map interface
- Dynamic loading of data based on zoom level
- Flow visualization with Bezier curves
- Selection and highlighting logic

## Configuration

The application uses 10 zoom levels with the following simplification factors:
- Level 1 (zoomed out): 5.0 (highest simplification)
- Level 10 (zoomed in): 0.5 (lowest simplification, most detail)

## Development

### Adding New Features
1. Extend the Flask API in `app.py` for backend functionality
2. Update the JavaScript in `templates/index.html` for frontend interactions
3. Consider the selection priority system (click > hover) when adding new interactions

### Performance Considerations
- The 10-level simplification system balances detail and performance
- Flow rendering is limited to prevent visual clutter
- Boundary loading is optimized based on current zoom level

## Dependencies

The following Python packages are required:

### Core Dependencies
- Flask: Web framework
- pandas: Data manipulation
- geopandas: Geospatial data processing
- shapely: Geometric operations
- numpy: Numerical operations

### Development Dependencies
- uv: Package manager

## API Endpoints

- `GET /` - Main application page
- `GET /api/boundaries?zoom={level}` - State boundaries for zoom level
- `GET /api/flows?min_flow={threshold}` - Migration flows above threshold
- `GET /api/net_migration?min_flow={threshold}` - Net migration flows
- `GET /api/state_migration/{state_name}` - Detailed migration data for state
- `GET /api/stats` - Overall migration statistics

## Troubleshooting

### Common Issues
1. **Missing Data Files**: Ensure `IND_5yrs_InternalMigFlows_2010.csv` and `india_states.geojson` are in the root directory
2. **Performance**: Large zoom levels or high flow thresholds may affect performance
3. **Coordinate Systems**: All data should use EPSG:4326 (WGS 84) coordinate system

### Browser Compatibility
- Modern browsers with JavaScript enabled
- Supports major browsers including Chrome, Firefox, Safari, Edge

## License

This project is released under the MIT License. See the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Future Enhancements

- Caching for boundaries and Bezier curve calculations
- Additional filtering options
- Export functionality
- Time-series visualization
- Additional geographic projections

## Authors

- Amit Portal

## Acknowledgments

- Migration data for research and analysis purposes
- Leaflet.js for interactive mapping capabilities
- OpenStreetMap for base map tiles