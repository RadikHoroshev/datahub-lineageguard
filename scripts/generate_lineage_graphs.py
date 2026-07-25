#!/usr/bin/env python3
"""Generate DataHub lineage visualization images for demo video."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json

DEMO_DIR = Path('/Users/radik/hackathons/datahub-lineageguard/demo_video')
GRAPHS_DIR = DEMO_DIR / 'lineage_graphs'
GRAPHS_DIR.mkdir(exist_ok=True)


def get_font(size: int = 24):
    """Get a monospace font, fallback to default if not available."""
    try:
        return ImageFont.truetype("/System/Library/Fonts/Monaco.ttf", size)
    except:
        try:
            return ImageFont.truetype("/System/Library/Fonts/Courier.ttc", size)
        except:
            return ImageFont.load_default()


def create_lineage_graph_with_tainted():
    """Create lineage graph highlighting tainted dataset in red."""
    width, height = 1920, 1080
    img = Image.new('RGB', (width, height), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    title_font = get_font(48)
    draw.text((width//2 - 400, 40), "DataHub Lineage Graph", fill='white', font=title_font)
    draw.text((width//2 - 350, 100), "fraud-features → fraud-detection-model → endpoint", 
              fill='#888888', font=get_font(28))
    
    nodes = {
        'customer-transactions': (200, 350),
        'transactions-v2-poisoned': (200, 550),
        'fraud-features': (600, 450),
        'fraud-feature-table': (1000, 450),
        'fraud-detection-model': (1400, 450),
        'fraud-model-endpoint': (1700, 450),
    }
    
    edge_color = '#444466'
    edges = [
        ('customer-transactions', 'fraud-features'),
        ('transactions-v2-poisoned', 'fraud-features'),
        ('fraud-features', 'fraud-feature-table'),
        ('fraud-feature-table', 'fraud-detection-model'),
        ('fraud-detection-model', 'fraud-model-endpoint'),
    ]
    
    for source, target in edges:
        x1, y1 = nodes[source]
        x2, y2 = nodes[target]
        color = '#ff4444' if source == 'transactions-v2-poisoned' else edge_color
        width_line = 4 if source == 'transactions-v2-poisoned' else 2
        draw.line([(x1 + 100, y1), (x2 - 100, y2)], fill=color, width=width_line)
        draw.polygon([(x2 - 100, y2), (x2 - 110, y2 - 5), (x2 - 110, y2 + 5)], fill=color)
    
    node_font = get_font(20)
    for name, (x, y) in nodes.items():
        is_tainted = name == 'transactions-v2-poisoned'
        box_width, box_height = 180, 80
        
        if is_tainted:
            draw.rounded_rectangle(
                [x - box_width//2, y - box_height//2,
                 x + box_width//2, y + box_height//2],
                radius=8, fill='#331111', outline='#ff4444', width=3)
        else:
            draw.rounded_rectangle(
                [x - box_width//2, y - box_height//2,
                 x + box_width//2, y + box_height//2],
                radius=8, fill='#16213e', outline='#4a4e69', width=2)
        
        label = name.replace('-', '\n')
        text_color = '#ff6666' if is_tainted else 'white'
        draw.text((x - 80, y - 20), label, fill=text_color, font=node_font)
        
        if is_tainted:
            badge_font = get_font(16)
            draw.text((x - 40, y + 25), "TAINTED", fill='#ff4444', font=badge_font)
            draw.polygon([(x + 50, y - 25), (x + 60, y - 5), (x + 40, y - 5)], fill='#ffaa00')
            draw.text((x + 45, y - 22), "!", fill='black', font=get_font(14))
    
    legend_y = 800
    draw.rectangle([100, legend_y, 500, legend_y + 150], fill='#0f0f23', outline='#444466', width=1)
    draw.text((120, legend_y + 20), "Legend:", fill='white', font=get_font(24))
    draw.rounded_rectangle([120, legend_y + 60, 160, legend_y + 90], radius=4, fill='#331111', outline='#ff4444', width=2)
    draw.text((170, legend_y + 65), "Tainted Dataset", fill='#ff6666', font=get_font(18))
    draw.rounded_rectangle([120, legend_y + 110, 160, legend_y + 140], radius=4, fill='#16213e', outline='#4a4e69', width=2)
    draw.text((170, legend_y + 115), "Normal Assets", fill='#8888aa', font=get_font(18))
    
    alert_y = 900
    draw.rounded_rectangle([100, alert_y, 900, alert_y + 80], radius=8, fill='#331111', outline='#ff4444', width=2)
    draw.text((120, alert_y + 20), "⚠️ CRITICAL: Tainted dataset 'transactions-v2-poisoned' feeds 5 downstream assets", 
              fill='#ff6666', font=get_font(22))
    draw.text((120, alert_y + 50), "    Impact: fraud-features → feature-table → model → endpoint", 
              fill='#ff8888', font=get_font(18))
    
    return img


def create_version_mismatch_comparison():
    """Create side-by-side version mismatch visualization."""
    width, height = 1920, 1080
    img = Image.new('RGB', (width, height), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    title_font = get_font(48)
    draw.text((width//2 - 450, 40), "Version Mismatch Detection", fill='white', font=title_font)
    draw.text((width//2 - 300, 100), "Trained Model vs Deployed Endpoint", fill='#888888', font=get_font(28))
    
    center_x = width // 2
    draw.line([(center_x, 160), (center_x, height - 100)], fill='#444466', width=2)
    
    left_center = center_x // 2
    draw.text((left_center - 200, 180), "TRAINED MODEL (MLflow)", fill='#44ff44', font=get_font(32))
    
    draw.rounded_rectangle([left_center - 250, 250, left_center + 250, 500], 
                          radius=12, fill='#113311', outline='#44ff44', width=3)
    
    model_font = get_font(36)
    draw.text((left_center - 150, 300), "fraud-detection-model", fill='white', font=model_font)
    draw.text((left_center - 80, 360), "Version:", fill='#88cc88', font=get_font(28))
    draw.text((left_center - 60, 400), "v1.2.3", fill='#44ff44', font=get_font(48))
    
    draw.text((left_center - 200, 550), "Platform: MLflow", fill='#aaaaaa', font=get_font(20))
    draw.text((left_center - 200, 580), "Status: Trained", fill='#aaaaaa', font=get_font(20))
    draw.text((left_center - 200, 610), "Date: 2024-07-20", fill='#aaaaaa', font=get_font(20))
    
    right_center = center_x + center_x // 2
    draw.text((right_center - 220, 180), "DEPLOYED ENDPOINT (SageMaker)", fill='#ff4444', font=get_font(32))
    
    draw.rounded_rectangle([right_center - 250, 250, right_center + 250, 500], 
                          radius=12, fill='#331111', outline='#ff4444', width=3)
    
    draw.text((right_center - 150, 300), "fraud-model-endpoint", fill='white', font=model_font)
    draw.text((right_center - 80, 360), "Version:", fill='#cc8888', font=get_font(28))
    draw.text((right_center - 60, 400), "v1.2.1", fill='#ff4444', font=get_font(48))
    
    draw.text((right_center - 200, 550), "Platform: SageMaker", fill='#aaaaaa', font=get_font(20))
    draw.text((right_center - 200, 580), "Status: Deployed", fill='#aaaaaa', font=get_font(20))
    draw.text((right_center - 200, 610), "Date: 2024-07-24", fill='#aaaaaa', font=get_font(20))
    
    arrow_y = 350
    for offset in range(0, 5):
        draw.line([(left_center + 50 + offset, arrow_y + offset), 
                   (center_x - 50 + offset, arrow_y + offset)], 
                  fill='#ffaa00', width=2)
    draw.polygon([(center_x - 50, arrow_y), (center_x - 70, arrow_y - 10), 
                  (center_x - 70, arrow_y + 10)], fill='#ffaa00')
    
    warning_y = 700
    draw.rounded_rectangle([300, warning_y, 1620, warning_y + 120], 
                          radius=10, fill='#332211', outline='#ffaa00', width=3)
    draw.text((400, warning_y + 20), "⚠️ HIGH RISK: Version Mismatch Detected", 
              fill='#ffaa00', font=get_font(32))
    draw.text((400, warning_y + 65), "Model v1.2.3 was trained but v1.2.1 is currently deployed", 
              fill='#ffcc88', font=get_font(24))
    draw.text((400, warning_y + 95), "Recommendation: Align deployment with trained model version or rollback", 
              fill='#88cc88', font=get_font(20))
    
    timeline_y = 880
    draw.text((100, timeline_y), "Deployment Timeline:", fill='#888888', font=get_font(24))
    draw.line([100, timeline_y + 60, 1800, timeline_y + 60], fill='#444466', width=3)
    
    events = [
        (300, "v1.2.1 deployed", '#ff4444'),
        (600, "v1.2.2 trained", '#444444'),
        (900, "v1.2.3 trained", '#44ff44'),
        (1200, "Still on v1.2.1!", '#ffaa00'),
    ]
    
    for x, label, color in events:
        draw.ellipse([x - 8, timeline_y + 52, x + 8, timeline_y + 68], fill=color, outline='white', width=2)
        draw.text((x - 60, timeline_y + 80), label, fill=color, font=get_font(16))
    
    return img


def create_complete_pipeline_graph():
    """Create complete pipeline lineage graph with all nodes."""
    width, height = 1920, 1080
    img = Image.new('RGB', (width, height), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    title_font = get_font(48)
    draw.text((width//2 - 350, 40), "Complete ML Pipeline Lineage", fill='white', font=title_font)
    draw.text((width//2 - 280, 100), "End-to-End DataFlow in DataHub", fill='#888888', font=get_font(28))
    
    stages = [
        ("Raw Data", ["customer-transactions", "transactions-v2-poisoned"], '#4a4e69'),
        ("Features", ["fraud-features"], '#5c6bc0'),
        ("Feature Store", ["fraud-feature-table"], '#7e57c2'),
        ("Model", ["fraud-detection-model", "shadow-fraud-model"], '#26a69a'),
        ("Endpoint", ["fraud-model-endpoint"], '#42a5f5'),
    ]
    
    stage_width = 300
    start_x = 150
    node_font = get_font(18)
    
    for i, (stage_name, nodes, color) in enumerate(stages):
        x = start_x + i * stage_width
        
        draw.text((x, 180), stage_name, fill='white', font=get_font(26))
        draw.line([(x, 215), (x + 250, 215)], fill=color, width=3)
        
        for j, node_name in enumerate(nodes):
            y = 280 + j * 150
            is_tainted = node_name == 'transactions-v2-poisoned'
            is_shadow = node_name == 'shadow-fraud-model'
            
            node_color = '#ff4444' if is_tainted else '#ffa726' if is_shadow else color
            bg_color = '#331111' if is_tainted else '#332211' if is_shadow else '#16213e'
            
            draw.rounded_rectangle([x, y, x + 250, y + 100], 
                                  radius=8, fill=bg_color, outline=node_color, width=2)
            
            label = node_name.replace('-', '\n')
            draw.text((x + 20, y + 25), label, fill='white', font=node_font)
            
            if is_tainted:
                draw.text((x + 20, y + 70), "⚠ TAINTED", fill='#ff6666', font=get_font(14))
            elif is_shadow:
                draw.text((x + 20, y + 70), "⚠ SHADOW", fill='#ffaa66', font=get_font(14))
    
    arrow_y = 330
    for i in range(len(stages) - 1):
        x1 = start_x + i * stage_width + 250
        x2 = start_x + (i + 1) * stage_width
        
        for offset in range(0, 3):
            draw.line([(x1 + offset, arrow_y + offset), (x2 - 10 + offset, arrow_y + offset)], 
                      fill='#44ff44', width=2)
        draw.polygon([(x2 - 10, arrow_y), (x2 - 20, arrow_y - 8), (x2 - 20, arrow_y + 8)], fill='#44ff44')
        
        if i == 0:
            tainted_y = 430
            for offset in range(0, 2):
                draw.line([(x1 + offset, tainted_y + offset), (x2 - 10 + offset, arrow_y + offset)], 
                          fill='#ff4444', width=2)
            draw.polygon([(x2 - 10, arrow_y), (x2 - 15, arrow_y - 5), (x2 - 15, arrow_y + 5)], fill='#ff4444')
    
    summary_y = 700
    draw.rounded_rectangle([100, summary_y, 1820, summary_y + 200], 
                          radius=10, fill='#0f0f23', outline='#444466', width=2)
    draw.text((150, summary_y + 20), "LineageGuard Scan Summary:", fill='white', font=get_font(28))
    
    issues = [
        ("CRITICAL", "Tainted dataset 'transactions-v2-poisoned' feeds downstream assets", '#ff4444'),
        ("HIGH", "Version mismatch: v1.2.3 trained vs v1.2.1 deployed", '#ffaa00'),
        ("MEDIUM", "Shadow model 'shadow-fraud-model' unregistered", '#ffa726'),
    ]
    
    for i, (level, desc, color) in enumerate(issues):
        y = summary_y + 70 + i * 45
        draw.text((170, y), f"[{level}]", fill=color, font=get_font(20))
        draw.text((320, y), desc, fill='#cccccc', font=get_font(18))
    
    return img


def create_datahub_ui_mock():
    """Create a mock DataHub UI screenshot with lineage graph."""
    width, height = 1920, 1080
    img = Image.new('RGB', (width, height), color='#f5f5f5')
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([0, 0, width, 60], fill='#ffffff', outline='#e0e0e0')
    draw.text((20, 15), "DataHub", fill='#333333', font=get_font(28))
    draw.text((120, 18), "Lineage", fill='#666666', font=get_font(22))
    
    draw.rounded_rectangle([400, 10, 800, 50], radius=4, fill='#f5f5f5', outline='#cccccc', width=1)
    draw.text((420, 20), "🔍 fraud-detection-model", fill='#999999', font=get_font(18))
    
    draw.rectangle([0, 60, 250, height], fill='#ffffff', outline='#e0e0e0')
    sidebar_items = ["Entities", "Datasets", "ML Models", "Lineage", "Validation"]
    for i, item in enumerate(sidebar_items):
        y = 100 + i * 50
        color = '#e3f2fd' if item == "Lineage" else '#ffffff'
        text_color = '#1976d2' if item == "Lineage" else '#666666'
        draw.rectangle([10, y, 240, y + 40], fill=color, outline='#e0e0e0')
        draw.text((30, y + 10), item, fill=text_color, font=get_font(18))
    
    graph_bg = '#fafafa'
    draw.rectangle([250, 60, width, height], fill=graph_bg)
    
    nodes = [
        (500, 400, "fraud-features", "Dataset", '#e3f2fd', '#1976d2'),
        (900, 400, "fraud-detection-model", "ML Model", '#e8f5e9', '#388e3c'),
        (1300, 400, "fraud-model-endpoint", "Endpoint", '#fff3e0', '#f57c00'),
    ]
    
    draw.line([(600, 400), (800, 400)], fill='#666666', width=2)
    draw.polygon([(800, 400), (790, 395), (790, 405)], fill='#666666')
    draw.line([(1000, 400), (1200, 400)], fill='#666666', width=2)
    draw.polygon([(1200, 400), (1210, 395), (1210, 405)], fill='#666666')
    
    draw.ellipse([350, 520, 450, 580], fill='#ffebee', outline='#c62828', width=3)
    draw.text((360, 545), "⚠", fill='#c62828', font=get_font(24))
    draw.line([(450, 550), (550, 450)], fill='#c62828', width=2)
    
    for x, y, name, node_type, bg_color, text_color in nodes:
        draw.rounded_rectangle([x - 100, y - 40, x + 100, y + 40], 
                              radius=8, fill=bg_color, outline=text_color, width=2)
        draw.text((x - 80, y - 15), name, fill='#333333', font=get_font(16))
        draw.text((x - 80, y + 5), node_type, fill=text_color, font=get_font(12))
    
    draw.rounded_rectangle([980, 360, 1050, 390], radius=4, fill='#ffebee', outline='#c62828', width=1)
    draw.text((990, 368), "v1.2.3", fill='#c62828', font=get_font(12))
    
    draw.rounded_rectangle([1380, 360, 1450, 390], radius=4, fill='#fff3e0', outline='#f57c00', width=1)
    draw.text((1390, 368), "v1.2.1", fill='#f57c00', font=get_font(12))
    
    legend_x, legend_y = 1600, 200
    draw.rounded_rectangle([legend_x, legend_y, legend_x + 200, legend_y + 150], 
                          radius=4, fill='#ffffff', outline='#cccccc', width=1)
    draw.text((legend_x + 10, legend_y + 10), "Legend", fill='#333333', font=get_font(18))
    draw.ellipse([legend_x + 20, legend_y + 50, legend_x + 40, legend_y + 70], fill='#ffebee', outline='#c62828', width=2)
    draw.text((legend_x + 50, legend_y + 55), "Tainted", fill='#666666', font=get_font(14))
    draw.ellipse([legend_x + 20, legend_y + 90, legend_x + 40, legend_y + 110], fill='#fff3e0', outline='#f57c00', width=2)
    draw.text((legend_x + 50, legend_y + 95), "Version Mismatch", fill='#666666', font=get_font(14))
    
    draw.text((350, 590), "transactions-v2-poisoned", fill='#c62828', font=get_font(14))
    draw.text((350, 610), "TAINTED", fill='#c62828', font=get_font(12))
    
    return img


def main():
    """Generate all lineage graph images."""
    print("Generating lineage graph visualizations...")
    
    img1 = create_lineage_graph_with_tainted()
    img1.save(GRAPHS_DIR / '01_lineage_with_tainted.png')
    print(f"✓ Saved: 01_lineage_with_tainted.png")
    
    img2 = create_version_mismatch_comparison()
    img2.save(GRAPHS_DIR / '02_version_mismatch.png')
    print(f"✓ Saved: 02_version_mismatch.png")
    
    img3 = create_complete_pipeline_graph()
    img3.save(GRAPHS_DIR / '03_complete_pipeline.png')
    print(f"✓ Saved: 03_complete_pipeline.png")
    
    img4 = create_datahub_ui_mock()
    img4.save(GRAPHS_DIR / '04_datahub_ui.png')
    print(f"✓ Saved: 04_datahub_ui.png")
    
    print(f"\nAll graphs saved to: {GRAPHS_DIR}")
    print(f"Total: 4 images generated")


if __name__ == "__main__":
    main()
