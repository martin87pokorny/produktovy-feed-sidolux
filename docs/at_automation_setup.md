# Airtable Automation: tlačítko "Regenerovat feed"

Návod jak v Airtable nastavit on-demand spouštění generátoru přes GitHub `workflow_dispatch`.

## 1. Vytvořit GitHub Personal Access Token (fine-grained)

1. https://github.com/settings/personal-access-tokens/new
2. Token name: `airtable-trigger-feed-regenerate`
3. Expiration: 1 rok
4. Repository access: Only select repositories → `martin87pokorny/produktovy-feed-sidolux`
5. Permissions:
   - Repository permissions → **Actions: Read and write**
   - Repository permissions → **Metadata: Read-only** (default)
6. Generate token → zkopírovat **(začíná `github_pat_…`)**, zobrazí se jen jednou

## 2. Uložit token v Airtable Automation secrets

V Airtable Automation editoru otevři Run a script action a vlož:

- AT nemá globální secret store; token musíš dát buď:
  - **Hardcoded v skriptu** (akceptovatelné u privátní base, ke které mají přístup jen oprávnění lidé)
  - Nebo do skrytého pole v config tabulce a načíst přes input variable

Pro tuto bázi (`appSIEtMDgBsBPpjS`) je hardcoded OK — token je fine-grained a omezený jen na tento jeden repo, write na Actions, nic jiného.

## 3. Nastavit Automation v AT

1. AT base → **Automations** → **Create automation** → název `Regenerovat feed (on-demand)`
2. **Trigger:**
   - Typ: **When record is updated**
   - Tabulka: `Feed_profile_index`
   - Watched field: `Status posl. běhu` se změní na `Pending`
   (Tlačítkový sloupec v interface pak nastavuje `Pending` → triggne automation)

3. **Action: Run a script:**

```javascript
// Trigger GitHub Actions workflow_dispatch pro regeneraci feedu.
// Token je fine-grained, omezen na repo martin87pokorny/produktovy-feed-sidolux,
// scope: Actions write.

const GITHUB_TOKEN = "ghp_VLOZ_TOKEN_SEM";
const REPO = "martin87pokorny/produktovy-feed-sidolux";
const WORKFLOW = "regenerate_feeds.yml";

const inputConfig = input.config();
const profileName = inputConfig.profilName || "all";

const url = `https://api.github.com/repos/${REPO}/actions/workflows/${WORKFLOW}/dispatches`;
const response = await fetch(url, {
    method: "POST",
    headers: {
        "Authorization": `Bearer ${GITHUB_TOKEN}`,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    },
    body: JSON.stringify({
        ref: "main",
        inputs: { profile: profileName }
    })
});

if (response.status === 204) {
    output.text(`✅ Regenerace profilu "${profileName}" zahájena. Hotovo do ~2 minut.`);
} else {
    const body = await response.text();
    output.text(`❌ HTTP ${response.status}: ${body}`);
    throw new Error(`GitHub dispatch failed: ${response.status}`);
}
```

4. **Input variables** (left panel):
   - `profilName` ← `Profil` field z triggered recordu
5. **Test** action s konkrétním záznamem.

## 4. Tlačítkový sloupec v Feed_profile_index

Aby Honza mohl klikat tlačítko, přidej do tabulky `Feed_profile_index` button field:

- Field type: **Button**
- Label: `🔄 Regenerovat`
- Action: **Run script** (Airtable extension) — alternativně **Open URL** s GitHub Actions UI URL pro daný workflow

Nebo (jednodušší): tlačítko **Update record** → změní `Status posl. běhu` na `Pending`. Tím se triggne automation z bodu 3. Generátor pak po doběhu přepíše status zpět na `OK`/`Warning`/`Error`.

## 5. Bezpečnost

- AT base je sdílená → token vlož jen ty (Honza), kdo má rights na admin
- Token rotuj 1× ročně (nebo když se mění tým)
- Pokud token kompromitován: revoke v https://github.com/settings/personal-access-tokens
- Generator skript má scope jen Actions write → nemůže pushnout kód, jen triggrovat workflow

## 6. Webhook (alternativa, pokud chceš real-time)

Místo polling triggeru lze použít AT webhook → GitHub repository_dispatch. Ale pro 1× za kvartál
změnu sortimentu je polling/manual úplně dostatečný.
