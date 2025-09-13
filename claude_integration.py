#!/usr/bin/env python3
"""
Standalone Claude Desktop Integration Module
To be imported into the main application
"""
import os
import json
from datetime import datetime
from flask import jsonify, render_template_string, request, session

def setup_claude_routes(app, logger=None):
    """Setup Claude Desktop integration routes on the Flask app"""
    
    @app.route('/claude/setup')
    def claude_setup_page():
        """Claude Desktop integration setup page"""
        # Get current server info
        port = app.config.get('PORT', int(os.getenv('FCC_PORT', '8000')))
        server_url = f"https://localhost:{port}"
        
        return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Desktop Integration - Financial Command Center AI</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --glass-bg: rgba(255, 255, 255, 0.08);
            --glass-border: rgba(255, 255, 255, 0.15);
            --success-color: #10b981;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            color: white;
            padding: 20px;
            margin: 0;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        
        .setup-card {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
        }
        
        .step-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }
        
        .step-number {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 30px;
            height: 30px;
            background: var(--primary-gradient);
            border-radius: 50%;
            font-weight: 600;
            margin-right: 15px;
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 12px 24px;
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 500;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .btn-primary {
            background: var(--primary-gradient);
            border-color: transparent;
        }
        
        .btn-success {
            background: linear-gradient(135deg, #10b981, #059669);
            border-color: transparent;
        }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        
        .alert-success {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #6ee7b7;
        }
        
        .command-example {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Connect to Claude Desktop</h1>
            <p>Enable AI-powered financial operations with voice commands</p>
        </div>
        
        <div class="setup-card">
            <div class="step-title">
                <span class="step-number">1</span>
                Generate MCP Server Configuration
            </div>
            <p>Click below to automatically generate your Claude Desktop configuration:</p>
            <br>
            <button class="btn btn-primary" onclick="generateConfig()">📄 Generate Config</button>
            <button class="btn btn-success" onclick="downloadConfig()" id="downloadBtn" style="display:none;">💾 Download Config</button>
        </div>
        
        <div class="setup-card">
            <div class="step-title">
                <span class="step-number">2</span>
                Try Sample Commands
            </div>
            <p>Once connected, try these AI commands in Claude Desktop:</p>
            
            <div class="command-example">
                <strong>💰 "Show me our cash flow this month"</strong><br>
                <em>Get real-time financial overview</em>
            </div>
            
            <div class="command-example">
                <strong>🧾 "List unpaid invoices over $1000"</strong><br>
                <em>Filter high-value outstanding payments</em>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="/" class="btn">🏠 Return to Dashboard</a>
        </div>
    </div>
    
    <script>
        let configData = null;
        
        async function generateConfig() {
            try {
                const response = await fetch('/api/claude/generate-config');
                const data = await response.json();
                
                if (data.success) {
                    configData = data.config;
                    document.getElementById('downloadBtn').style.display = 'inline-flex';
                    
                    const alert = document.createElement('div');
                    alert.className = 'alert alert-success';
                    alert.innerHTML = '✅ Configuration generated! Click Download to save it.';
                    document.querySelector('.setup-card').appendChild(alert);
                }
            } catch (error) {
                alert('Failed to generate configuration: ' + error);
            }
        }
        
        function downloadConfig() {
            if (!configData) {
                alert('Please generate configuration first.');
                return;
            }
            
            const blob = new Blob([configData], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'claude_desktop_config.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    </script>
</body>
</html>
        ''', server_url=server_url)

    @app.route('/api/claude/generate-config')
    def generate_claude_config():
        """Generate Claude Desktop MCP configuration"""
        try:
            # Get current server configuration
            port = int(os.getenv('FCC_PORT', '8000'))
            server_url = f"https://localhost:{port}"
            
            # Generate configuration
            config = {
                "mcpServers": {
                    "financial-command-center": {
                        "command": "python",
                        "args": [
                            "-m",
                            "http",
                            "--url",
                            f"{server_url}/api/mcp"
                        ],
                        "env": {
                            "FCC_SERVER_URL": server_url,
                            "FCC_API_KEY": "claude-desktop-integration"
                        }
                    }
                }
            }
            
            config_json = json.dumps(config, indent=2)
            
            return jsonify({
                'success': True,
                'config': config_json,
                'server_url': server_url,
                'message': 'Configuration generated successfully'
            })
            
        except Exception as e:
            if logger:
                logger.error(f"Claude config generation error: {e}")
            return jsonify({
                'success': False,
                'message': f'Configuration generation error: {str(e)}'
            }), 500

    @app.route('/api/mcp', methods=['GET', 'POST'])
    def mcp_endpoint():
        """MCP server endpoint for Claude Desktop integration"""
        try:
            if request.method == 'GET':
                # Return available tools/capabilities
                return jsonify({
                    'tools': [
                        {
                            'name': 'get_financial_health',
                            'description': 'Get overall financial health and system status'
                        },
                        {
                            'name': 'get_invoices', 
                            'description': 'Retrieve invoices with optional filtering'
                        },
                        {
                            'name': 'get_contacts',
                            'description': 'Get customer/supplier contact information'
                        }
                    ]
                })
            
            # Handle MCP tool calls
            data = request.get_json()
            tool_name = data.get('tool')
            
            if tool_name == 'get_financial_health':
                return jsonify({
                    'result': {
                        'status': 'healthy',
                        'health_percentage': 95,
                        'message': 'All systems operational'
                    }
                })
            
            return jsonify({'error': f'Tool {tool_name} not implemented yet'}), 501
            
        except Exception as e:
            if logger:
                logger.error(f"MCP endpoint error: {e}")
            return jsonify({'error': f'MCP endpoint error: {str(e)}'}), 500

    return "Claude Desktop routes registered successfully"