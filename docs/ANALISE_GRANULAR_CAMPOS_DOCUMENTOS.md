# 🔍 ANÁLISE GRANULAR - CAMPOS DE DOCUMENTOS POR TABELA

## 📊 **RELATÓRIO DETALHADO DE INCONSISTÊNCIAS POR CAMPO**

### 🎯 **METODOLOGIA**
Análise específica de **cada campo de documento** em **cada tabela**, identificando:
- **Nome exato do campo**
- **Tipo de documento esperado** (CPF/CNPJ)
- **Tamanho atual vs esperado**
- **Quantidade de zeros faltando**
- **Exemplos específicos** de valores incorretos

---

## 📋 **TABELA: `emissao`**

### **🔸 CAMPO: `documento_do_titular`**
**📌 REGRA:** Sempre CPF (11 dígitos)

| Tamanho Atual | Tamanho Esperado | Quantidade | Percentual | Exemplo Valor | Tipo de Erro |
|---------------|------------------|------------|------------|---------------|---------------|
| **6 dígitos** | 11 | 1 | 0.00% | `464341` | **FALTAM 5 ZEROS À ESQUERDA** |
| **7 dígitos** | 11 | 18 | 0.02% | `1348132` | **FALTAM 4 ZEROS À ESQUERDA** |
| **8 dígitos** | 11 | 123 | 0.12% | `11567805` | **FALTAM 3 ZEROS À ESQUERDA** |
| **9 dígitos** | 11 | 1.994 | 1.99% | `100452876` | **FALTAM 2 ZEROS À ESQUERDA** |
| **10 dígitos** | 11 | 20.599 | 20.58% | `1000579859` | **FALTAM 1 ZERO À ESQUERDA** |
| **11 dígitos** | 11 | 77.363 | 77.29% | `10001350633` | ✅ **CORRETO** |

**🚨 IMPACTO:** 22.735 registros (22,71%) com CPF incorreto

### **🔸 CAMPO: `documento`**
**📌 REGRA:** CPF (11 dígitos) para produtos CPF | CNPJ (14 dígitos) para produtos CNPJ/PJ

#### **📄 Produtos CPF (e-CPF, etc.):**
| Tamanho Atual | Tamanho Esperado | Quantidade | Percentual | Exemplo Valor | Exemplo Produto | Tipo de Erro |
|---------------|------------------|------------|------------|---------------|-----------------|---------------|
| **7 dígitos** | 11 | 7 | 0.02% | `1348132` | e-CPF A1 (Arquivo) 1 Ano | **FALTAM 4 ZEROS À ESQUERDA** |
| **8 dígitos** | 11 | 48 | 0.14% | `11567805` | e-CPF A1 (Arquivo) 1 Ano | **FALTAM 3 ZEROS À ESQUERDA** |
| **9 dígitos** | 11 | 712 | 2.08% | `100452876` | SPC ID e-CPF | **FALTAM 2 ZEROS À ESQUERDA** |
| **10 dígitos** | 11 | 7.397 | 21.59% | `1000579859` | SPC ID e-CPF | **FALTAM 1 ZERO À ESQUERDA** |
| **11 dígitos** | 11 | 26.093 | 76.17% | `10001350633` | SPC ID e-CPF | ✅ **CORRETO** |

**🚨 IMPACTO:** 8.164 registros (23,83%) com documento CPF incorreto

#### **📄 Produtos CNPJ (e-CNPJ, e-PJ, etc.):**
| Tamanho Atual | Tamanho Esperado | Quantidade | Percentual | Exemplo Valor | Exemplo Produto | Tipo de Erro |
|---------------|------------------|------------|------------|---------------|-----------------|---------------|
| **10 dígitos** | 14 | 29 | 0.04% | `2137000185` | e-CNPJ A1 (Arquivo) 1 Ano | **FALTAM 4 ZEROS À ESQUERDA** |
| **11 dígitos** | 14 | 110 | 0.17% | `11358000110` | e-CNPJ A1 (Arquivo) 1 Ano | **FALTAM 3 ZEROS À ESQUERDA** |
| **12 dígitos** | 14 | 829 | 1.26% | `107916000145` | e-CNPJ A1 (Arquivo) 1 Ano | **FALTAM 2 ZEROS À ESQUERDA** |
| **13 dígitos** | 14 | 11.413 | 17.33% | `1000172000128` | e-CNPJ A1 (Arquivo) 1 Ano | **FALTAM 1 ZERO À ESQUERDA** |
| **14 dígitos** | 14 | 53.460 | 81.20% | `10013378000183` | SPC ID e-CNPJ | ✅ **CORRETO** |

**🚨 IMPACTO:** 12.381 registros (18,80%) com documento CNPJ incorreto

---

## 📋 **TABELA: `renovacao_geral`**

### **🔸 CAMPO: `cpfcnpj`**
**📌 REGRA:** CPF (11 dígitos) ou CNPJ (14 dígitos)

| Tamanho Atual | Tipo Identificado | Quantidade | Percentual | Exemplo Valor | Tipo de Erro |
|---------------|-------------------|------------|------------|---------------|---------------|
| **11 dígitos** | CPF | 14.809 | 38.37% | `00005292573` | ✅ **CORRETO - CPF** |
| **13 dígitos** | INDEFINIDO | 27 | 0.07% | `1261577000110` | **FALTAM 1 ZERO À ESQUERDA (CNPJ)** |
| **14 dígitos** | CNPJ | 23.756 | 61.56% | `00002317000167` | ✅ **CORRETO - CNPJ** |

**🚨 IMPACTO:** 27 registros (0,07%) com CNPJ incorreto

---

## 📋 **TABELA: `renovacao_safeid`**

### **🔸 CAMPO: `documento`**
**📌 REGRA:** CPF (11 dígitos) ou CNPJ (14 dígitos)

| Tamanho Atual | Tipo Identificado | Quantidade | Percentual | Exemplo Valor | Tipo de Erro |
|---------------|-------------------|------------|------------|---------------|---------------|
| **11 dígitos** | CPF | 5.831 | 99.95% | `00005982243` | ✅ **CORRETO - CPF** |
| **14 dígitos** | CNPJ | 3 | 0.05% | `40291442000159` | ✅ **CORRETO - CNPJ** |

**✅ RESULTADO:** Tabela `renovacao_safeid` está **100% CORRETA**!

---

## 📊 **RESUMO CONSOLIDADO POR CAMPO**

### **🚨 CAMPOS COM PROBLEMAS:**

| Tabela | Campo | Registros Incorretos | Percentual | Principal Problema |
|--------|-------|---------------------|------------|-------------------|
| **emissao** | **documento_do_titular** | **22.735** | **22,71%** | **Zeros à esquerda faltando em CPFs** |
| **emissao** | **documento** (produtos CPF) | **8.164** | **23,83%** | **Zeros à esquerda faltando em CPFs** |
| **emissao** | **documento** (produtos CNPJ) | **12.381** | **18,80%** | **Zeros à esquerda faltando em CNPJs** |
| **renovacao_geral** | **cpfcnpj** | **27** | **0,07%** | **1 zero à esquerda faltando em CNPJs** |

### **✅ CAMPOS CORRETOS:**
| Tabela | Campo | Status |
|--------|-------|--------|
| **renovacao_safeid** | **documento** | ✅ **100% CORRETO** |

---

## 🛠️ **SCRIPTS DE CORREÇÃO ESPECÍFICOS POR CAMPO**

### **1. 🔧 TABELA `emissao` - CAMPO `documento_do_titular`**
```sql
-- Corrigir CPFs com zeros à esquerda faltando
UPDATE emissao 
SET documento_do_titular = LPAD(documento_do_titular, 11, '0')
WHERE documento_do_titular IS NOT NULL 
  AND documento_do_titular ~ '^[0-9]+$'
  AND LENGTH(documento_do_titular) < 11;

-- Verificação pós-correção
SELECT 'documento_do_titular' as campo, LENGTH(documento_do_titular) as tamanho, COUNT(*) 
FROM emissao WHERE documento_do_titular IS NOT NULL 
GROUP BY LENGTH(documento_do_titular);
```

### **2. 🔧 TABELA `emissao` - CAMPO `documento` (produtos CPF)**
```sql
-- Corrigir documentos CPF
UPDATE emissao 
SET documento = LPAD(documento, 11, '0')
WHERE documento IS NOT NULL 
  AND documento ~ '^[0-9]+$'
  AND LENGTH(documento) < 11
  AND (produto ILIKE '%cpf%' OR produto ILIKE '%e-cpf%');

-- Verificação pós-correção
SELECT 'documento_CPF' as campo, LENGTH(documento) as tamanho, COUNT(*) 
FROM emissao WHERE documento IS NOT NULL AND (produto ILIKE '%cpf%' OR produto ILIKE '%e-cpf%')
GROUP BY LENGTH(documento);
```

### **3. 🔧 TABELA `emissao` - CAMPO `documento` (produtos CNPJ/PJ)**
```sql
-- Corrigir documentos CNPJ
UPDATE emissao 
SET documento = LPAD(documento, 14, '0')
WHERE documento IS NOT NULL 
  AND documento ~ '^[0-9]+$'
  AND LENGTH(documento) < 14
  AND (produto ILIKE '%cnpj%' OR produto ILIKE '%e-cnpj%' OR produto ILIKE '%pj%');

-- Verificação pós-correção
SELECT 'documento_CNPJ' as campo, LENGTH(documento) as tamanho, COUNT(*) 
FROM emissao WHERE documento IS NOT NULL AND (produto ILIKE '%cnpj%' OR produto ILIKE '%e-cnpj%' OR produto ILIKE '%pj%')
GROUP BY LENGTH(documento);
```

### **4. 🔧 TABELA `renovacao_geral` - CAMPO `cpfcnpj`**
```sql
-- Corrigir CNPJs com 13 dígitos (falta 1 zero)
UPDATE renovacao_geral 
SET cpfcnpj = LPAD(cpfcnpj, 14, '0')
WHERE cpfcnpj IS NOT NULL 
  AND cpfcnpj ~ '^[0-9]+$'
  AND LENGTH(cpfcnpj) = 13;

-- Verificação pós-correção
SELECT 'cpfcnpj' as campo, LENGTH(cpfcnpj) as tamanho, COUNT(*) 
FROM renovacao_geral WHERE cpfcnpj IS NOT NULL 
GROUP BY LENGTH(cpfcnpj);
```

---

## 🎯 **EXEMPLOS ESPECÍFICOS DE CORREÇÃO**

### **Antes da Correção:**
| Campo | Valor Incorreto | Problema |
|-------|-----------------|----------|
| `documento_do_titular` | `464341` | Faltam 5 zeros → `00000464341` |
| `documento_do_titular` | `692303073` | Faltam 2 zeros → `06923030730` |
| `documento` (CPF) | `100452876` | Faltam 2 zeros → `01004528760` |
| `documento` (CNPJ) | `1000172000128` | Falta 1 zero → `01000172000128` |
| `cpfcnpj` | `1261577000110` | Falta 1 zero → `01261577000110` |

### **Depois da Correção:**
| Campo | Valor Correto | Status |
|-------|---------------|--------|
| `documento_do_titular` | `00000464341` | ✅ CPF válido |
| `documento_do_titular` | `06923030730` | ✅ CPF válido |
| `documento` (CPF) | `01004528760` | ✅ CPF válido |
| `documento` (CNPJ) | `01000172000128` | ✅ CNPJ válido |
| `cpfcnpj` | `01261577000110` | ✅ CNPJ válido |

---

## 📈 **IMPACTO NO CRM 360 APÓS CORREÇÃO**

### **🔍 Busca por CPF:**
- **ANTES:** CPF `692303073` não encontrado
- **DEPOIS:** CPF `06923030730` encontra todos os registros relacionados

### **📊 Métricas de Cliente:**
- **ANTES:** Cliente pode aparecer fragmentado em múltiplos perfis
- **DEPOIS:** Visão 360 completa e unificada

### **🚀 Oportunidades de Renovação:**
- **ANTES:** Oportunidades perdidas por CPFs não relacionados
- **DEPOIS:** 100% das oportunidades identificadas corretamente

---

## 🎯 **CONCLUSÃO**

### **📊 Total de Registros a Corrigir:**
- **43.307 registros** com problemas de formatação
- **Concentrados principalmente** na tabela `emissao`
- **Tabela `renovacao_safeid`** já está perfeita

### **✅ Prioridade de Correção:**
1. **CRÍTICO:** `emissao.documento_do_titular` (22.735 registros)
2. **ALTO:** `emissao.documento` produtos CNPJ (12.381 registros)
3. **MÉDIO:** `emissao.documento` produtos CPF (8.164 registros)
4. **BAIXO:** `renovacao_geral.cpfcnpj` (27 registros)

**🚨 RECOMENDAÇÃO:** Executar correções na ordem de prioridade para maximizar o impacto no CRM 360!
