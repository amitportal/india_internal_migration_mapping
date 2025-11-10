"""
Flask-based Interactive Migration Map Application
Main application file
"""
from flask import Flask, render_template, jsonify, request
import pandas as pd
import geopandas as gpd
import json
import numpy as np
from shapely.geometry import Point
import math

app = Flask(__name__)

# Load data once at startup
print("Loading data...")
df = pd.read_csv("IND_5yrs_InternalMigFlows_2010.csv")
states = gpd.read_file("india_states.geojson").to_crs(epsg=4326)

# Create 10 levels of simplified geometries for different zoom levels
# Based on the provided scaling table, where higher "scale" value means larger area visible (more zoomed out)
# The scaling factor likely represents level of simplification needed
# Level 0 (zoom 1): most generalization (scaling factor 5.0 -> simplification 0.2)
# Level 9 (zoom 10): least generalization (scaling factor 0.5 -> simplification 0.01)
simplification_levels = []

# The table suggests that as we zoom in (higher zoom level), we want less simplification (more detail)
# So zoom level 1 corresponds to max simplification, zoom level 10 to min simplification
# Map scaling factors to appropriate simplification values for Shapely
factor_mapping = [
    0.20,   # Level 0: zoom 1, scaling factor 5.0 -> high simplification
    0.18,   # Level 1: zoom 2, scaling factor 4.5
    0.15,   # Level 2: zoom 3, scaling factor 4.0
    0.12,   # Level 3: zoom 4, scaling factor 3.5
    0.10,   # Level 4: zoom 5, scaling factor 3.0
    0.08,   # Level 5: zoom 6, scaling factor 2.5
    0.06,   # Level 6: zoom 7, scaling factor 2.0
    0.04,   # Level 7: zoom 8, scaling factor 1.5
    0.02,   # Level 8: zoom 9, scaling factor 1.0
    0.0001  # Level 9: zoom 10, scaling factor 0.5 -> low simplification (most detail)
]

for i in range(10):
    simplification_factor = factor_mapping[i]
    simplified_states = states.copy()
    simplified_states['geometry'] = states['geometry'].simplify(simplification_factor)
    simplification_levels.append(simplified_states)

# Process migration data to match with states
origins = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df['LONFR'], df['LATFR']), crs="EPSG:4326"
)
destinations = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df['LONTO'], df['LATTO']), crs="EPSG:4326"
)

# Spatial join to assign state names
origins_joined = gpd.sjoin(origins, states[['state', 'geometry']], how="left", predicate="within")
destinations_joined = gpd.sjoin(destinations, states[['state', 'geometry']], how="left", predicate="within")

df['origin_state'] = origins_joined['state']
df['dest_state'] = destinations_joined['state']

# Remove rows with missing state assignments
df = df.dropna(subset=['origin_state', 'dest_state'])

# Remove self-flows
df = df[df['origin_state'] != df['dest_state']]

# Aggregate flows by state pairs
flows = df.groupby(['origin_state', 'dest_state'], as_index=False)['PrdMIG'].sum()
flows = flows.sort_values('PrdMIG', ascending=False)

# Calculate migration metrics
in_mig = flows.groupby('dest_state')['PrdMIG'].sum()
out_mig = flows.groupby('origin_state')['PrdMIG'].sum()
net_mig = in_mig.subtract(out_mig, fill_value=0)

# Calculate centroids for flow visualization
states_projected = states.to_crs(epsg=32643)
state_centroids_projected = states_projected.set_index('state').geometry.centroid
state_centroids = gpd.GeoSeries(state_centroids_projected, crs=states_projected.crs).to_crs(epsg=4326)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/boundaries')
def get_boundaries():
    """API endpoint to get boundaries based on zoom level (10 levels)"""
    zoom = request.args.get('zoom', 5, type=int)
    
    # Map zoom level (1-10) to simplification level (0-9)
    # Higher zoom = more detail = lower simplification index
    simplification_index = min(9, max(0, zoom - 1))  # Ensure index is between 0-9
    
    # Get the appropriate simplified geometry
    simplified_states = simplification_levels[simplification_index]
    
    # Convert to GeoJSON
    geojson_data = json.loads(simplified_states.to_json())
    
    # Add migration data to features
    for feature in geojson_data['features']:
        state_name = feature['properties']['state']
        feature['properties']['net_mig'] = int(net_mig.get(state_name, 0))
        feature['properties']['in_mig'] = int(in_mig.get(state_name, 0))
        feature['properties']['out_mig'] = int(out_mig.get(state_name, 0))
    
    return jsonify(geojson_data)

@app.route('/api/flows')
def get_flows():
    """API endpoint to get migration flows"""
    min_flow = request.args.get('min_flow', 0, type=float)
    flow_type = request.args.get('type', 'all')  # all, in, out
    
    # Filter flows based on parameters
    filtered_flows = flows[flows['PrdMIG'] >= min_flow].copy()
    
    # Calculate centroids for each flow
    flow_data = []
    for _, row in filtered_flows.iterrows():
        origin_state = row['origin_state']
        dest_state = row['dest_state']
        
        if origin_state in state_centroids.index and dest_state in state_centroids.index:
            origin_point = state_centroids[origin_state]
            dest_point = state_centroids[dest_state]
            
            flow_data.append({
                'origin_state': origin_state,
                'dest_state': dest_state,
                'origin_coords': [origin_point.x, origin_point.y],  # [lon, lat]
                'dest_coords': [dest_point.x, dest_point.y],        # [lon, lat]
                'flow_value': float(row['PrdMIG']),
                'in_mig': int(in_mig.get(dest_state, 0)),
                'out_mig': int(out_mig.get(origin_state, 0)),
                'net_mig': int(net_mig.get(origin_state, 0))
            })
    
    # Limit number of flows returned for performance
    flow_data = sorted(flow_data, key=lambda x: x['flow_value'], reverse=True)[:200]
    
    return jsonify(flow_data)

@app.route('/api/stats')
def get_stats():
    """API endpoint to get overall statistics"""
    total_flows = int(flows['PrdMIG'].sum())
    num_states = len(net_mig)
    max_net = int(net_mig.max()) if len(net_mig) > 0 else 0
    min_net = int(net_mig.min()) if len(net_mig) > 0 else 0
    
    return jsonify({
        'total_migration': total_flows,
        'num_states': num_states,
        'max_net_migration': max_net,
        'min_net_migration': min_net,
        'num_flows': len(flows)
    })

@app.route('/api/state_migration/<state_name>')
def get_state_migration(state_name):
    """API endpoint to get migration details for a specific state"""
    # Get out-migration from this state
    out_flows = flows[flows['origin_state'] == state_name]
    # Get in-migration to this state  
    in_flows = flows[flows['dest_state'] == state_name]
    
    # Calculate totals
    total_out = float(out_flows['PrdMIG'].sum()) if len(out_flows) > 0 else 0
    total_in = float(in_flows['PrdMIG'].sum()) if len(in_flows) > 0 else 0
    net_mig = total_in - total_out
    
    # Prepare detailed flow data
    out_details = []
    for _, row in out_flows.iterrows():
        out_details.append({
            'to_state': row['dest_state'],
            'flow_value': float(row['PrdMIG'])
        })
    
    in_details = []
    for _, row in in_flows.iterrows():
        in_details.append({
            'from_state': row['origin_state'],
            'flow_value': float(row['PrdMIG'])
        })
    
    return jsonify({
        'state': state_name,
        'total_out': total_out,
        'total_in': total_in,
        'net_mig': net_mig,
        'out_flows': out_details,
        'in_flows': in_details
    })

@app.route('/api/net_migration')
def get_net_migration():
    """API endpoint to get net migration flows between states"""
    min_flow = request.args.get('min_flow', 0, type=float)
    
    # Calculate net migration between each pair of states
    # For each state pair, we calculate net flow (in - out)
    state_pairs = set()
    
    # Add all state pairs from both origin and destination
    for _, row in flows.iterrows():
        pair = tuple(sorted([row['origin_state'], row['dest_state']]))
        state_pairs.add(pair)
    
    net_flows = []
    for pair in state_pairs:
        state_a, state_b = pair
        
        # Calculate flow from A to B
        flow_a_to_b = flows[
            (flows['origin_state'] == state_a) & (flows['dest_state'] == state_b)
        ]['PrdMIG'].sum()
        
        # Calculate flow from B to A
        flow_b_to_a = flows[
            (flows['origin_state'] == state_b) & (flows['dest_state'] == state_a)
        ]['PrdMIG'].sum()
        
        # Calculate net flow (positive means A to B, negative means B to A)
        net_flow = flow_a_to_b - flow_b_to_a
        
        if abs(net_flow) >= min_flow:
            # Determine direction - if positive, A to B; if negative, B to A (with positive value)
            if net_flow > 0:
                from_state, to_state = state_a, state_b
                flow_value = net_flow
            else:
                from_state, to_state = state_b, state_a
                flow_value = abs(net_flow)
                
            net_flows.append({
                'from_state': from_state,
                'to_state': to_state,
                'net_flow': flow_value,
                'direction': 1 if net_flow > 0 else -1  # 1 for original direction, -1 for reversed
            })
    
    return jsonify(net_flows)

if __name__ == '__main__':
    print("Starting migration visualization app...")
    app.run(debug=True, host='0.0.0.0', port=5000)