#!/usr/bin/env python3
"""
Download planetary ephemerides from JPL Horizons and save to HDF5 file.
"""

from astroquery.jplhorizons import Horizons
import h5py
import numpy as np
from datetime import datetime
from pathlib import Path

__OUTPUT_DIR__ = Path('../data/')

# Define planets and their NAIF ID codes
planets = {
    'Sun': '10',
    'Mercury': '199',
    'Venus': '299', 
    'Earth': '399',
    'Jupiter': '599',
    'Saturn': '699',
    'Uranus': '799',
    'Neptune': '899'
}

# Time range
epochs = {
    'start': '1931-01-01',
    'stop': '2025-12-30',
    'step': '1d'
}

print(f"Downloading ephemerides from {epochs['start']} to {epochs['stop']}")
print(f"Planets: {', '.join(planets.keys())}")
print("-" * 70)

# Create HDF5 file
output_path = __OUTPUT_DIR__ / 'PlanetaryEphemerides.h5'
print(f"Creating hdf5 file as {output_path}")
with h5py.File(output_path, 'w') as f:
    # Add metadata
    f.attrs['start_date'] = epochs['start']
    f.attrs['stop_date'] = epochs['stop']
    f.attrs['step_size'] = epochs['step']
    f.attrs['coordinate_center'] = '@sun (heliocentric)'
    f.attrs['reference_frame'] = 'ecliptic J2000'
    f.attrs['creation_date'] = datetime.now().isoformat()
    
    # Download data for each planet
    for name, id_code in planets.items():
        print(f"Downloading {name}...", end=' ', flush=True)
        
        try:
            # Query Horizons
            obj = Horizons(
                id=id_code,
                location='500@10',
                epochs=epochs
            )
            
            # Get vectors (position and velocity)
            vec = obj.vectors(refplane='ecliptic')
            
            # Extract data
            jd = vec['datetime_jd']
            x  = vec['x']
            y  = vec['y']
            z  = vec['z']
            vx = vec['vx']
            vy = vec['vy']
            vz = vec['vz']
            
            # Create group for this planet
            grp = f.create_group(name)
            
            # Store data
            grp.create_dataset('jd', data=jd, compression='gzip')
            grp.create_dataset('x', data=x, compression='gzip')
            grp.create_dataset('y', data=y, compression='gzip')
            grp.create_dataset('z', data=z, compression='gzip')
            grp.create_dataset('vx', data=vx, compression='gzip')
            grp.create_dataset('vy', data=vy, compression='gzip')
            grp.create_dataset('vz', data=vz, compression='gzip')
            
            # Add metadata
            grp.attrs['naif_id'] = id_code
            grp.attrs['units_position'] = str(x.unit)
            grp.attrs['units_velocity'] = str(vx.unit)
            grp.attrs['n_points'] = len(jd)
            
            print(f"Done ({len(jd)} points)")
            
        except Exception as e:
            print(f"✗ ERROR: {e}")
            continue

print("-" * 70)
print("Ephemerides saved to: PlanetaryEphemerides.h5")

# Print summary
print("\nFile contents:")
with h5py.File(output_path, 'r') as f:
    print(f"Groups: {list(f.keys())}")
    for planet in f.keys():
        n_points = f[planet].attrs['n_points']
        print(f"  {planet}: {n_points} data points")