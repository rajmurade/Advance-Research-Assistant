# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from src.workflow import Workflow

load_dotenv()


def main():
    workflow = Workflow()
    print("Developer Tools Research Agent")

    while True:
        query = input("\n🔍 Developer Tools Query: ").strip()
        if query.lower() in {"quit", "exit"}:
            break

        if query:
            result = workflow.run(query)
            print(f"\n📊 Results for: {query}")
            print("=" * 60)

            if result.request_type == "code" and result.code_result:
                cr = result.code_result
                print(f"   🔤 Language: {cr.language or 'python'}")
                print("   ▶️  Execution Status:", "Executed" if cr.executed else "Not executed")
                print(f"   🔁 Attempts: {cr.execution_count}")
                if cr.retries:
                    print(f"   🛠️  Corrected after {cr.retries} error(s)")

                print("\n   Code:")
                print("-" * 40)
                print(cr.code)

                if cr.executed:
                    print("\n   Execution Output:")
                    print("-" * 40)
                    print(cr.output or "(no output)")

                if cr.error:
                    print("\n   Execution Error:")
                    print("-" * 40)
                    print(cr.error)

                if cr.explanation:
                    print("\n   Explanation:")
                    print("-" * 40)
                    print(cr.explanation)
                print()

            else:
                for i, company in enumerate(result.companies, 1):
                    print(f"\n{i}. 🏢 {company.name}")
                    print(f"   🌐 Website: {company.website}")
                    print(f"   💰 Pricing: {company.pricing_model}")
                    print(f"   📖 Open Source: {company.is_open_source}")

                    if company.tech_stack:
                        print(f"   🛠️  Tech Stack: {', '.join(company.tech_stack[:5])}")

                    if company.language_support:
                        print(
                            f"   💻 Language Support: {', '.join(company.language_support[:5])}"
                        )

                    if company.api_available is not None:
                        api_status = (
                            "✅ Available" if company.api_available else "❌ Not Available"
                        )
                        print(f"   🔌 API: {api_status}")

                    if company.integration_capabilities:
                        print(
                            f"   🔗 Integrations: {', '.join(company.integration_capabilities[:4])}"
                        )

                    if company.description and company.description != "Analysis failed":
                        print(f"   📝 Description: {company.description}")

                    print()

                if result.analysis:
                    print("Developer Recommendations: ")
                    print("-" * 40)
                    print(result.analysis)


if __name__ == "__main__":
    main()
