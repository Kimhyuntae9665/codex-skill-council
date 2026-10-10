"""Rebuild the editable logo diagram; optional CairoSVG PNG export. No network."""
import argparse
import base64
import hashlib
import html
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / 'docs/images'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def render() -> Path:
    graph = json.loads((IMAGES / 'council-flow.graph.json').read_text(encoding='utf-8'))
    assets = json.loads((IMAGES / 'logo-assets.json').read_text(encoding='utf-8'))
    width, height = graph['width'], graph['height']
    esc = html.escape
    parts = [f'<svg xmlns="{NS}" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
             f'<title id="title">{esc(graph["title"])}</title><desc id="desc">{esc(graph["description"])}</desc>',
             '<defs><pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#354054"/></pattern><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#a9b5c8"/></marker></defs>',
             f'<rect width="{width}" height="{height}" fill="#141b28"/><rect width="{width}" height="{height}" fill="url(#dots)"/>']
    positions = {n['id']: (n['x'], n['y']) for n in graph['nodes']}
    for edge in graph['edges']:
        x, y = positions[edge['source']]
        tx, ty = positions[edge['target']]
        sx, sy, ey = x + 100, y + 50, ty + 50
        if tx <= sx:
            raise ValueError('Diagram requires forward edges with card separation')
        mid = (sx + tx) / 2
        parts.append(f'<path d="M{sx} {sy}C{mid} {sy} {mid} {ey} {tx} {ey}" fill="none" stroke="#a9b5c8" stroke-width="2" marker-end="url(#arrow)"/>')
    for node in graph['nodes']:
        entry = assets[node['asset']]
        path = (IMAGES / entry['path']).resolve()
        if not path.is_relative_to(IMAGES.resolve()):
            raise ValueError('Asset path escaped image directory')
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry['sha256']:
            raise ValueError('Asset hash mismatch')
        mark = ET.fromstring(raw)
        if any(e.tag.split('}')[-1] not in {'svg', 'path', 'g', 'title'} for e in mark.iter()):
            raise ValueError('Unexpected content in the pinned standalone mark')
        mark.set('width', '320')
        mark.set('height', '320')
        mark.set('color', '#000000')
        data = base64.b64encode(ET.tostring(mark, encoding='utf-8')).decode('ascii')
        x, y = node['x'], node['y']
        parts.append(f'<g aria-label="{esc(entry["name"])}"><rect x="{x}" y="{y}" width="100" height="100" rx="18" fill="#ffffff" stroke="#78879d" stroke-width="1.5"/><image x="{x+18}" y="{y+18}" width="64" height="64" href="data:image/svg+xml;base64,{data}"/><text x="{x+50}" y="{y+126}" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="500" fill="#e3e9f2">{esc(entry["name"])}</text></g>')
    parts.append('</svg>')
    output = IMAGES / 'council-flow.svg'
    output.write_text(''.join(parts) + '\n', encoding='utf-8', newline='\n')
    print(f'SVG: {output}')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--png', action='store_true', help='Requires an already available CairoSVG renderer')
    args = parser.parse_args()
    svg = render()
    if args.png:
        import cairosvg
        output = svg.with_suffix('.png')
        cairosvg.svg2png(url=str(svg), write_to=str(output), output_width=1600)
        print(f'PNG: {output}')
