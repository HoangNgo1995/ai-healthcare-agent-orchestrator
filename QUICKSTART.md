# Quick Deployment Guide - GPT-4o Vision (GPU-Free)

## Tóm Tắt Nhanh

Deployment này sử dụng **GPT-4o Vision** cho phân tích ảnh y tế, **KHÔNG cần GPU**.

**Ưu điểm:**

- ✅ Tiết kiệm ~90-95% chi phí infrastructure
- ✅ Deployment nhanh hơn (10-15 phút vs 20-30 phút)
- ✅ Không cần GPU quota
- ✅ Đơn giản hơn, ít lỗi hơn

## Các Bước Deployment

### Bước 1: Kiểm Tra Requirements

**Bạn CẦN:**

- ✅ Azure subscription
- ✅ Azure OpenAI quota: GPT-4o (100K+ TPM)
- ✅ Owner permissions trên một resource group
- ✅ Azure CLI & Azure Developer CLI đã cài

**Bạn KHÔNG CẦN:**

- ❌ GPU quota (không cần NCADSA100v4 hay NCADSH100v5)
- ❌ Azure ML quota
- ❌ HLS model endpoints

### Bước 2: Authenticate

```bash
# Login to Azure
az login

# Login to Azure Developer CLI
azd auth login

# (Optional) Nếu có multiple tenants
# az login -t <TENANT_ID>
# azd auth login --tenant <TENANT_ID>
```

### Bước 3: Tạo Environment

```bash
# Tạo environment mới (tên ngắn ≤ 8 ký tự)
azd env new dev

# Hoặc tên khác
# azd env new prod
# azd env new demo
```

### Bước 4: Set Variables (Nếu Cần)

**CƠ BẢN** - Không cần set gì cả nếu:

- Dùng 1 region cho tất cả resources
- Không cần thêm IP cho App Service access

**NÂNG CAO** - Chỉ set nếu cần:

```bash
# Nếu muốn dùng GPT-4o ở region khác AZURE_LOCATION
azd env set AZURE_GPT_LOCATION eastus

# Nếu muốn App Service ở region khác
azd env set AZURE_APPSERVICE_LOCATION westus

# Nếu cần access từ IP riêng (cho development)
azd env set ADDITIONAL_ALLOWED_IPS "your.ip.address/32"

# Nếu dùng FHIR hoặc Fabric thay vì Blob Storage
azd env set CLINICAL_NOTES_SOURCE fhir  # hoặc fabric
```

**QUAN TRỌNG**:

- ❌ KHÔNG cần set `AZURE_HLS_LOCATION` (GPU location)
- ❌ KHÔNG cần set `GPU_INSTANCE_TYPE`
- Các biến này chỉ dùng cho CxrReportGen (đã không dùng nữa)

### Bước 5: Deploy!

```bash
azd up
```

**Trong quá trình deploy:**

1. **Chọn subscription**: Pick subscription bạn muốn deploy vào
2. **Chọn region**: Pick region có GPT-4o quota
3. **Chọn resource group**: Tạo mới hoặc dùng existing
4. **Chọn principal type**: Chọn **User**

**Deployment sẽ:**

- ✅ Tạo Azure OpenAI service với GPT-4o deployment
- ✅ Tạo App Service cho backend
- ✅ Tạo Storage accounts cho patient data
- ✅ Tạo Bot services và managed identities
- ✅ Deploy radiology_vision plugin (GPT-4o Vision)
- ⏱️ Mất khoảng 10-15 phút

**Output sau khi deploy:**

```
Deploying services (azd deploy)

  (✓) Done: Deploying service web
  - Endpoint: https://app-xxxxx.azurewebsites.net

SUCCESS: Your application was provisioned and deployed to Azure in X minutes Y seconds.
You can view the resources created under the resource group rg-xxxxx in Azure Portal:
https://portal.azure.com/#@/resource/subscriptions/.../resourceGroups/rg-xxxxx/overview
```

Lưu lại **Endpoint URL** để dùng sau!

### Bước 6: Install Agents vào Teams

**Lấy Teams Chat ID:**

1. Mở Teams chat/meeting muốn dùng
2. Click "..." → "Get link to chat"
3. Copy phần sau `https://teams.microsoft.com/l/chat/`

**Upload agents:**

```bash
# Bash (Linux/Mac/WSL)
./scripts/uploadPackage.sh ./output <CHAT_ID>

# PowerShell (Windows)
.\scripts\uploadPackage.ps1 -directory ./output -chatOrMeeting <CHAT_ID>
```

**Ví dụ:**

```bash
./scripts/uploadPackage.sh ./output 19:abcd1234-5678-9012-3456-789012345678_efgh5678@unq.gbl.spaces
```

### Bước 7: Test!

**Test trong Teams:**

```
@Orchestrator Can you start a tumor board review for Patient ID: patient_4?
```

**Test Radiology Agent:**

```
@Radiology analyze the x-ray for patient_4
```

**Expected behavior:**

- Agent sẽ announce: "I have used GPT-4o Vision to analyze..."
- Trả về structured radiology findings
- Conclude với: "back to you: Orchestrator"

**Test Web UI:**

- Mở endpoint URL (từ Bước 5)
- Default chỉ access được từ Microsoft IP ranges
- Để access từ máy local: set `ADDITIONAL_ALLOWED_IPS` và redeploy

## Troubleshooting

### Issue: "Insufficient quota for GPT-4o"

**Giải pháp:**

```bash
# Check quota
az cognitiveservices account list-skus \
  --name <openai-account-name> \
  --resource-group <rg-name>

# Request quota increase tại:
# https://portal.azure.com → Azure OpenAI → Quotas
```

### Issue: "Deployment failed"

**Giải pháp:**

```bash
# Clean up và retry
azd down --purge
azd up
```

### Issue: "Cannot access web UI"

**Giải pháp:**

```bash
# Add your IP
azd env set ADDITIONAL_ALLOWED_IPS "$(curl -s ifconfig.me)/32"
azd up
```

### Issue: "Agents not appearing in Teams"

**Giải pháp:**

1. Verify packages được upload: Check `./output` folder
2. Verify Teams admin allows custom apps
3. Try manual upload: Teams → Apps → Upload a custom app
4. See [docs/teams.md](docs/teams.md)

## Verification Checklist

Sau khi deploy, verify:

- [ ] ✅ `azd up` completed successfully
- [ ] ✅ Web endpoint accessible (từ allowed IPs)
- [ ] ✅ Agents uploaded to Teams
- [ ] ✅ `@Orchestrator` responds in Teams
- [ ] ✅ `@Radiology` can analyze images
- [ ] ✅ No errors in Azure Portal → App Service → Logs

## Cost Estimation

**Monthly costs (estimated):**

| Component           | Cost                |
| ------------------- | ------------------- |
| GPT-4o API calls    | $100-300            |
| App Service (P1mv3) | $150-200            |
| Storage accounts    | $10-20              |
| Bot services        | Minimal             |
| **Total**           | **~$300-500/month** |

**So sánh với GPU deployment:**

- GPU deployment: ~$2,500-3,500/month
- **Savings: 85-90%** 🎉

## Next Steps

1. **Customize agents**: Edit `src/scenarios/default/config/agents.yaml`
2. **Add patient data**: Upload to Storage account
3. **Configure FHIR**: See [docs/fhir_integration.md](docs/fhir_integration.md)
4. **Setup evaluation**: See [docs/evaluation.md](docs/evaluation.md)
5. **Review architecture**: See [docs/radiology_gpt4o_vision.md](docs/radiology_gpt4o_vision.md)

## Resources

- **Full Documentation**: [README.md](README.md)
- **Radiology Details**: [docs/radiology_gpt4o_vision.md](docs/radiology_gpt4o_vision.md)
- **Troubleshooting**: [docs/troubleshooting.md](docs/troubleshooting.md)
- **User Guide**: [docs/user_guide.md](docs/user_guide.md)

---

**Questions?** Create a [GitHub issue](https://github.com/Azure-Samples/healthcare-agent-orchestrator/issues) or email hlsfrontierteam@microsoft.com

**Last Updated**: January 30, 2026
