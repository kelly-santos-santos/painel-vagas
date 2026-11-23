import datetime
import json
import urllib.parse
import urllib.request

KEYWORDS = [
    "Analista de CRM",
    "Analista de Marketing",
    "Excelencia Comercial",
    "Analista de Comunicacao",
]

PRIORITY_COMPANIES = [
    "bayer", "roche", "novartis", "sanofi", "astrazeneca", "pfizer", "gsk",
    "abbvie", "johnson", "novo nordisk", "lilly", "takeda", "msd", "boehringer",
    "itau", "santander", "bradesco", "nubank", "btg", "picpay", "c6",
    "microsoft", "google", "amazon", "salesforce", "adobe", "oracle", "sap", "ibm", "meta",
    "mercado livre", "shopee", "ifood", "magazine luiza", "natura", "boticario"
]

def score_job(job):
    text = f"{job.get('name', '')} {job.get('description', '')}".lower()
    score = 0
    # 1. Experiencia relevante (25)
    if any(k in text for k in ["crm", "veeva", "salesforce", "regua", "relacionamento"]):
        score += 24
    elif any(k in text for k in ["marketing", "comunicacao", "campanha"]):
        score += 18
    # 2. Competencias tecnicas (20)
    tech_hits = sum(1 for k in ["excel", "kpi", "segmentacao", "automacao", "dados", "ia", "newsletter"] if k in text)
    score += min(20, 10 + tech_hits * 3)
    # 3. Responsabilidades (20)
    if any(k in text for k in ["relatorio", "painel", "forca de vendas", "fornecedor", "processo"]):
        score += 17
    else:
        score += 13
    # 4. Senioridade (15)
    if any(k in text for k in ["junior", "jr", "assistente"]):
        score += 15
    elif "pleno" in text:
        score += 9
    elif any(k in text for k in ["senior", "sr", "iii", "gerente", "coordenador"]):
        score += 5
    else:
        score += 11
    # 5. Segmento (10)
    company = job.get("careerPageName", "").lower()
    score += 10 if any(c in company for c in PRIORITY_COMPANIES) else 6
    # 6. Formacao e idiomas (5)
    score += 1 if "ingles avancado" in text or "ingles fluente" in text else 5
    # 7. Modelo/localizacao (5)
    city = (job.get("city") or "").lower()
    if job.get("isRemoteWork") or "sao paulo" in city or "são paulo" in city or "osasco" in city:
        score += 5
    else:
        score += 1
    return min(100, score)

def fetch_gupy(term):
    url = "https://portal.gupy.io/api/v1/jobs?jobName=" + urllib.parse.quote(term) + "&limit=10"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8")).get("data", [])

def main():
    with open("vagas.json", "r", encoding="utf-8") as f:
        store = json.load(f)

    existing = store.get("vagas", [])
    seen_links = {v["link"] for v in existing}
    today = datetime.datetime.now().strftime("%d/%m/%Y")
    next_idx = len(existing) + 1

    for term in KEYWORDS:
        try:
            items = fetch_gupy(term)
        except Exception as e:
            print(f"Erro ao buscar '{term}': {e}")
            continue
        for item in items:
            link = item.get("jobUrl")
            if not link or link in seen_links:
                continue
            seen_links.add(link)
            nota = score_job(item)
            status = "PARA AVALIAR" if nota >= 65 else "DESCARTADA"
            existing.append({
                "id": f"VAGA-{next_idx:03d}",
                "dataBusca": today,
                "dataCandidatura": "Não informado",
                "dataPublicacao": (item.get("publishedDate") or "")[:10] or "Não informado",
                "dataFechamento": (item.get("applicationDeadline") or "")[:10] or "Não informado",
                "nome": item.get("name", "Vaga sem título"),
                "empresa": item.get("careerPageName", "Não informado"),
                "link": link,
                "fonte": "Gupy (API pública)",
                "local": f"{item.get('city') or 'Remoto'}/{item.get('state') or ''}".strip("/"),
                "modelo": "Remoto" if item.get("isRemoteWork") else (item.get("workplaceType") or "Não informado"),
                "salario": "Salário não informado",
                "nota": nota,
                "classificacao": "Compatibilidade excelente" if nota >= 90 else ("Compatibilidade alta" if nota >= 80 else ("Boa compatibilidade" if nota >= 70 else ("Compatibilidade limítrofe" if nota >= 65 else "Descartar"))),
                "status": status,
                "motivoCompatibilidade": "Avaliação automática baseada nos 7 critérios do perfil-base.",
                "principaisGaps": "Validar requisitos detalhados na página oficial.",
                "motivoDescarte": f"Compatibilidade de {nota}% (< 65 pontos)." if nota < 65 else "",
                "ultimaAtualizacao": today,
                "proximaAcao": f"Aguardando aprovação (OK VAGA-{next_idx:03d})" if nota >= 65 else "Descartada (< 65 pontos)",
                "prazo": (item.get("applicationDeadline") or "")[:10] or "Não informado"
            })
            next_idx += 1

    existing.sort(key=lambda x: x.get("nota", 0), reverse=True)
    store["vagas"] = existing
    store["atualizadoEm"] = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M")
    with open("vagas.json", "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
