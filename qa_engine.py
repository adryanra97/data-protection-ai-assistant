from langchain.memory import ConversationBufferMemory
from langchain_openai import AzureChatOpenAI
from config import settings

class QAEngine:
    def __init__(self, tools: dict):
        self.tools = tools
        self.llm = AzureChatOpenAI(
            openai_api_key=settings.OPENAI_CHAT_API_KEY,
            azure_endpoint=settings.CHAT_OPENAI_API_BASE,
            openai_api_version="2024-12-01-preview",
            azure_deployment=settings.CHAT_MODEL_NAME,
            temperature=0
        )
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.search_cfg = {"k": 3, "score_threshold": 0.7}
        self.ATTEMPT_COUNTER = {}

    def query_tools(self, query: str):
        tool_prompt = (
            f"Pertanyaan pengguna:\n{query}\n\n"
            "Dari daftar tools berikut:\n"
            "- gdpr → regulasi GDPR\n"
            "- pdp → UU PDP\n"
            "- company → kebijakan internal\n"
            "- tavily → fallback pencarian\n\n"
            "Contoh: ['gdpr'] atau ['tavily']"
        )
        selection = self.llm.invoke([
            {"role": "system", "content": "Pilih tools relevan."},
            {"role": "user", "content": tool_prompt}
        ])

        try:
            selected = eval(selection.content.strip())
        except:
            selected = ['tavily']

        results = {}
        for key in selected:
            if key in self.tools:
                res = self.tools[key].func(query)
                if res:
                    results[key] = res

        if not results and 'tavily' not in selected:
            fallback = self.tools['tavily'].func(query)
            if fallback:
                results["tavily"] = fallback

        return results

    def answer(self, query: str) -> str:
        cnt = self.ATTEMPT_COUNTER.get(query, 0)
        chunks = self.query_tools(query)
        if not chunks:
            if cnt < 2:
                self.ATTEMPT_COUNTER[query] = cnt + 1
                return "Maaf, belum ada info. Bisa berikan detail tambahan?"
            self.ATTEMPT_COUNTER[query] = 0
            note = "Catatan: ini dari GPT-4o, bukan dokumen."
            resp = self.llm.invoke([
                {"role": "system", "content": "Anda adalah Legal Expert."},
                {"role": "user", "content": query}
            ])
            return f"{note}\n\n{resp.content}"

        self.ATTEMPT_COUNTER[query] = 0
        content = "\n\n".join(chunks.values())

        if list(chunks.keys()) == ["tavily"]:
            relevance_check = self.llm.invoke([
                {"role": "system", "content": "Anda evaluator relevansi."},
                {"role": "user", "content": f"Relevansi untuk: {query}\n\nTeks:\n{content}"}
            ])
            if 'tidak relevan' in relevance_check.content.lower():
                return "Maaf, belum ada info relevan. Bisa beri detail tambahan?"

        prompt = "Teks sumber:\n" + content
        final_msgs = self.memory.chat_memory.messages + [
            {"role": "system", "content": "Anda adalah Legal Expert..."},
            {"role": "user", "content": prompt}
        ]
        resp = self.llm.invoke(final_msgs)
        self.memory.chat_memory.add_user_message(prompt)
        self.memory.chat_memory.add_ai_message(resp.content)
        return resp.content

    def reset_memory(self):
        self.memory.chat_memory.messages.clear()
