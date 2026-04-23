---
tags: [security, aws, iam, study-guide, index, learning-path]
created: 2026-04-23
---

# 📖 AWS IAM 학습 가이드 — 시리즈 허브

> 💡 **한줄 요약**: AWS IAM(Identity and Access Management)의 4대 구성요소(User, Group, Policy, Role)를 개별 심층 분석하고, 실제 운영 환경에서의 유기적 결합까지 다루는 6개 문서 시리즈의 진입점.

---

## 📚 전체 문서 목록

### 학습 시리즈 (번호순)

| # | 문서 | 핵심 내용 |
|---|------|----------|
| 01 | [[01-aws-iam-user-concept-explainer]] | IAM User, 자격증명(Password/Access Key/MFA), Root vs IAM User, IAM Identity Center 비교 |
| 02 | [[02-aws-iam-group-concept-explainer]] | User 집합, 직무 기반 권한 일괄 관리, 중첩 불가 제약, Principal 아님 |
| 03 | [[03-aws-iam-policy-concept-explainer]] | JSON 정책 구조(Effect/Action/Resource/Condition), 7가지 정책 유형, 평가 로직 |
| 04 | [[04-aws-iam-role-concept-explainer]] | AssumeRole/STS 임시 자격증명, Trust Policy, Instance Profile, OIDC Federation, 혼동된 대리인 |
| 05 | [[05-aws-iam-concept-explainer]] | IAM 전체 개요, 4대 구성요소 관계, 인증 vs 인가, 3대 클라우드 IAM 비교 |
| 06 | [[06-aws-iam-architecture-and-integration]] | 4요소 유기적 결합, 온보딩/CI-CD/Cross-Account/멀티계정 시나리오, Terraform 코드, CIS 보안 체크리스트 |

### 관련 문서

| 문서 | 위치 | 내용 |
|------|------|------|
| [[sso-concept-explainer]] | security/ | SSO (Single Sign-On) Deep Dive |
| [[oauth2-concept-explainer]] | security/ | OAuth 2.0 Deep Dive |
| [[sso-oauth-comparison-and-architecture]] | security/ | SSO-OAuth 비교 + Google SSO 아키텍처 |

---

## 🗺️ 읽기 순서

```
                    ┌──────────────────────────────┐
                    │  여기 (00 허브 페이지)        │
                    └──────────────┬───────────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
           ▼                       ▼                       ▼
  ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
  │ 🔰 입문 코스   │   │ ⚡ 속성 코스   │   │ 🎯 실무 코스   │
  │ (처음부터)     │   │ (개념 아는 분) │   │ (바로 적용)    │
  └───────┬────────┘   └───────┬────────┘   └───────┬────────┘
          │                    │                     │
          ▼                    ▼                     ▼
  01 User (사원증)     05 IAM 전체 개요      06 통합 문서
          │                    │              (시나리오 +
          ▼                    ▼               Terraform +
  02 Group (부서)      03 Policy (규칙)       체크리스트)
          │                    │
          ▼                    ▼
  03 Policy (규칙)     04 Role (임시증)
          │                    │
          ▼                    ▼
  04 Role (임시증)     06 통합 문서
          │
          ▼
  05 IAM 전체 개요
          │
          ▼
  06 통합 문서
```

---

## 🎯 레벨별 추천 경로

### 🔰 입문자 (AWS IAM 처음)

> "IAM이 뭔지 모르겠어요"

1. **01 User** → 가장 구체적인 개념(사원증)으로 시작
2. **02 Group** → User를 묶는 방법 이해
3. **03 Policy** → 권한을 정의하는 JSON 문서 이해
4. **04 Role** → 가장 추상적인 개념(임시 신원) 이해
5. **05 IAM 전체** → 4요소가 어떻게 합쳐지는지 조망
6. **06 통합** → 실제 시나리오로 체화

### ⚡ 속성 코스 (개념은 알지만 깊이가 부족)

> "User, Role 이런 건 아는데 Policy 평가 로직이 헷갈려요"

1. **05 IAM 전체** → 전체 그림 빠르게 리프레시
2. **03 Policy** → 평가 로직, 7가지 정책 유형 이해
3. **04 Role** → Trust Policy, 혼동된 대리인 문제
4. **06 통합** → Terraform 코드로 실전 감각

### 🎯 실무 코스 (당장 AWS 설정해야 할 때)

> "Terraform으로 IAM 구성해야 하는데 어떻게?"

1. **06 통합** → 시나리오별 아키텍처 + Terraform 코드 + CIS 체크리스트
2. 필요한 개념만 01~05에서 역참조

---

## 🔑 핵심 비유 한눈에

| # | 개념 | 비유 | 핵심 특성 |
|---|------|------|----------|
| 01 | **User** | 🪪 사원증 | 장기 자격증명, 1인 1계정 |
| 02 | **Group** | 🏫 반(Class) | User 집합, 권한 일괄 상속 |
| 03 | **Policy** | 📋 이용 규칙표 | JSON 문서, Allow/Deny 결정 |
| 04 | **Role** | 🎭 스태프 조끼 | 임시 자격증명, 입었다 벗는다 |
| 05 | **IAM** | 🏢 빌딩 보안 시스템 | 인증 + 인가 + 감사 |
| 06 | **통합** | 🔧 보안 운영 매뉴얼 | 시나리오별 실전 가이드 |
