"""
Verify Harness

Agentic Engineering의 Verify 단계를 담당한다.
AI Action(코드 구현) 이후, 사람이 최종 리뷰하기 전에 아래 순서로 자동 검증한다.

1. Test Verify   : pytest 전체 스위트 실행 (Regression + Correctness)
2. Compliance Verify : 현재 Phase의 docs/design/phaseN.md 요구사항과 docs/PLAN.md 체크리스트를
                       사람이 대조 확인하도록 안내 문구를 출력한다 (자동 판정은 하지 않음 - 최종 판단은 사람의 몫).

Test Verify가 실패하면 Compliance Verify 단계로 진행하지 않고 종료한다.
"""
import subprocess
import sys


def run_test_verify() -> bool:
    print("=== [1/2] Test Verify: pytest 전체 스위트 실행 ===")
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])
    return result.returncode == 0


def run_compliance_verify() -> None:
    print("\n=== [2/2] Compliance Verify ===")
    print("아래 항목을 docs/PLAN.md, docs/design/phaseN.md와 대조하여 사람이 직접 확인하세요:")
    print("  1. 이번 변경이 해당 Phase의 설계 문서(docs/design/phaseN.md) 범위를 벗어나지 않는가")
    print("  2. docs/PLAN.md의 해당 Phase 체크리스트 항목을 모두 충족하는가")
    print("  3. 콘솔에서 직접 실행하여 실제 동작을 눈으로 확인했는가 (E2E 수동 검증)")
    print("  4. Commit 전 docs/REPORT.md에 이번 작업 보고서가 작성되었는가")


def main() -> None:
    if not run_test_verify():
        print("\nTest Verify 실패: pytest가 실패했습니다. Compliance Verify로 진행하지 않습니다.")
        sys.exit(1)
    run_compliance_verify()
    print("\nVerify Harness 통과. 사람의 최종 리뷰 및 커밋을 진행하세요.")


if __name__ == "__main__":
    main()
