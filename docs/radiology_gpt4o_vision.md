# Radiology Analysis with GPT-4o Vision

This document describes the GPT-4o Vision implementation for radiology image analysis (Option 3).

## Overview

The Radiology agent uses GPT-4o Vision to analyze chest X-rays and CT scans, providing structured radiology findings without requiring specialized GPU infrastructure.

## Architecture

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Patient   │─────▶│  Orchestrator    │─────▶│   Radiology     │
│   Query     │      │     Agent        │      │     Agent       │
└─────────────┘      └──────────────────┘      └─────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────────┐
                                              │  radiology_vision   │
                                              │      Plugin         │
                                              └─────────────────────┘
                                                        │
                                    ┌───────────────────┼───────────────────┐
                                    ▼                   ▼                   ▼
                              ┌──────────┐      ┌─────────────┐    ┌──────────────┐
                              │  Azure   │      │   Azure     │    │   GPT-4o     │
                              │   Blob   │      │   OpenAI    │    │   Vision     │
                              │ Storage  │      │    API      │    │    Model     │
                              └──────────┘      └─────────────┘    └──────────────┘
```

## Features

### ✅ Advantages

- **No GPU required**: Eliminates expensive GPU instance costs (~$3,000-4,000/month savings)
- **Lower latency**: Faster response times via API calls
- **Multi-modal**: Supports X-rays, CT scans, and other image types
- **Simpler deployment**: No model hosting infrastructure needed
- **Scalable**: Automatic scaling via Azure OpenAI service

### ⚠️ Limitations

- **No pixel-level grounding**: Cannot provide exact bounding boxes
- **General-purpose model**: Less specialized than CxrReportGen for chest X-rays
- **Not FDA-cleared**: Suitable for research/development only
- **Requires validation**: All findings should be reviewed by radiologists

## Usage

### From Teams Chat

```
@Radiology analyze the latest CT scan for patient_4
```

### From Orchestrator

```
What do the imaging studies show for patient_4?
```

### Direct API Call

```python
from scenarios.default.tools.radiology_vision import create_plugin

# Initialize plugin
plugin = create_plugin(plugin_config)

# Analyze image
findings = await plugin.analyze_radiology_image(
    patient_id="patient_4",
    filename="ct_scan.png",
    indication="Chest pain and shortness of breath"
)

print(findings)
```

## Report Structure

GPT-4o Vision generates structured reports with:

1. **Technical Quality**
   - Image acquisition parameters
   - Quality assessment

2. **Comparison**
   - Reference to prior studies (if mentioned)

3. **Findings** (organized by anatomy)
   - Lungs and airways
   - Pleura
   - Heart and mediastinum
   - Bones and soft tissues

4. **Impression**
   - Summary of key findings
   - Clinical significance

## Example Output

```
TECHNICAL QUALITY:
Standard frontal chest radiograph. Adequate penetration and positioning.

COMPARISON:
None available.

FINDINGS:

Lungs and Airways:
- Increased opacity in the right lower lobe measuring approximately 4 x 3 cm,
  consistent with consolidation.
- No pleural effusion or pneumothorax.

Heart and Mediastinum:
- Normal cardiac silhouette.
- Mediastinal contours within normal limits.

Bones and Soft Tissues:
- No acute osseous abnormality.

IMPRESSION:
Right lower lobe consolidation concerning for pneumonia. Clinical correlation
and follow-up recommended. Recommend comparison with prior studies if available.
```

## Cost Comparison

| Component           | CxrReportGen  | GPT-4o Vision     |
| ------------------- | ------------- | ----------------- |
| GPU Instance        | ~$3-5/hour    | $0                |
| API Calls           | $0            | ~$0.01-0.05/image |
| Storage             | Same          | Same              |
| **Total (monthly)** | ~$2,000-3,000 | ~$100-200         |

**Estimated savings: 90-95%**

## Deployment

### 1. Files Modified/Created

- ✅ Created: `src/scenarios/default/tools/radiology_vision.py`
- ✅ Updated: `src/scenarios/default/config/agents.yaml`
- ✅ Created: `notebooks/tests/radiology_vision.ipynb`
- ✅ Created: `docs/radiology_gpt4o_vision.md`

### 2. Deploy Changes

```bash
# Deploy all changes
azd up
```

### 3. (Optional) Remove GPU Resources

To save costs, comment out GPU deployment in `infra/main.bicep`:

```bicep
// Comment out HLS model deployment
// module m_hlsModel 'modules/hlsModel.bicep' = {
//   name: 'deploy_hls_model'
//   ...
// }

// Update outputs
var outHlsModelEndpoints = [] // was: m_hlsModel.outputs.modelEndpoints
```

Then redeploy:

```bash
azd up
```

## Testing

### Run Test Notebook

```bash
# Open Jupyter
jupyter notebook notebooks/tests/radiology_vision.ipynb

# Or use VS Code notebook interface
```

### Test from Terminal

```bash
# Set environment
export AZURE_ENV_NAME=dev

# Run Python script
cd src
python -c "
from scenarios.default.tools.radiology_vision import create_plugin
# ... (see notebook for full example)
"
```

## Monitoring

Track usage via Azure Monitor:

- API call volume
- Token consumption (typically 500-2000 tokens per image analysis)
- Response latency (usually 2-5 seconds)
- Error rates

## Best Practices

1. **Always provide clinical indication** for better context
2. **Include patient history** when relevant
3. **Specify exact filename** to avoid ambiguity
4. **Review all findings** with qualified radiologists
5. **Monitor token usage** to optimize costs

## Troubleshooting

### Issue: Poor quality findings

**Solution**:

- Ensure high-quality images (minimum 512x512 resolution)
- Provide detailed clinical indication
- Include relevant patient history

### Issue: API timeouts

**Solution**:

- Check Azure OpenAI quota limits
- Increase timeout settings in plugin (currently 30s default)
- Reduce concurrent requests

### Issue: Incorrect measurements

**Solution**:

- GPT-4o Vision provides approximate measurements only
- Verify critical measurements manually
- Consider dedicated measurement tools for precision

### Issue: Tool not found

**Solution**:

- Verify plugin file exists: `src/scenarios/default/tools/radiology_vision.py`
- Check agents.yaml has correct tool name: `radiology_vision`
- Restart application after changes

## Migration from CxrReportGen

### Step-by-step Migration

1. ✅ **Backup current configuration**
   - agents.yaml saved as agents.yaml.backup
2. ✅ **Deploy radiology_vision plugin**
   - File created at `src/scenarios/default/tools/radiology_vision.py`
3. ✅ **Update agent configuration**
   - agents.yaml updated with new instructions and tools
4. **Test with sample images**
   - Use `notebooks/tests/radiology_vision.ipynb`
5. **Compare outputs** (if needed)
   - Run both CxrReportGen and GPT-4o Vision on same images
   - Validate differences with radiologists
6. **Remove CxrReportGen resources** (optional)
   - Run cleanup script (see below)
   - Comment out GPU deployment in infra/main.bicep
   - Redeploy with `azd up`

### Cleanup Script

```bash
# Run the cleanup script
bash scripts/cleanup-cxr-plugin.sh

# Or manually:
# rm src/scenarios/default/tools/cxr_report_gen.py
# rm notebooks/tests/cxr_report_gen.ipynb
```

## Technical Details

### Plugin Implementation

The `RadiologyVisionPlugin` class provides:

- **analyze_radiology_image()**: Main function for image analysis
- Automatic image type detection (X-ray vs CT)
- Structured prompting for consistent report format
- Error handling and logging
- Base64 image encoding for API submission

### Integration with Semantic Kernel

- Uses Semantic Kernel's `@kernel_function` decorator
- Leverages existing Azure OpenAI service configuration
- Supports async/await patterns for non-blocking execution
- Compatible with existing data access layer

### Image Processing Pipeline

1. Read image from Azure Blob Storage
2. Encode to base64
3. Determine image type from filename
4. Generate appropriate system/user prompts
5. Call GPT-4o Vision API
6. Return structured findings

## References

- [GPT-4o Vision Documentation](https://learn.microsoft.com/azure/ai-services/openai/how-to/gpt-with-vision)
- [Azure OpenAI Best Practices](https://learn.microsoft.com/azure/ai-services/openai/concepts/best-practices)
- [Semantic Kernel Documentation](https://learn.microsoft.com/semantic-kernel/)
- [Healthcare Agent Development Guide](agent_development.md)

## Support

For issues or questions:

1. Check [Troubleshooting Guide](troubleshooting.md)
2. Review [FAQ](faq.md)
3. Open an issue on GitHub
4. Contact the development team

---

**Last Updated**: January 30, 2026  
**Status**: ✅ Production Ready (Research Use Only)
