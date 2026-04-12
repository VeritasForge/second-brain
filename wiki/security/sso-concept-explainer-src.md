---
type: source
origin: ingest
confidence: medium
date_created: 2026-04-09
source_path: "[[raw/sources/2026-04-09-sso-concept-explainer]]"
tags: [sso, authentication, security]
---

# SSO (Single Sign-On) — Source Card

## 요약

SSO(Single Sign-On)에 대한 8관점 concept-explainer 심층 분석 리포트.

- **정의**: 한 번의 로그인으로 여러 서비스에 접근할 수 있게 해주는 인증 메커니즘
- **핵심 구성**: User, Identity Provider (IdP), Service Provider (SP), Authentication Token
- **구현 프로토콜**: SAML 2.0, OAuth 2.0, OIDC (신규 표준)
- **비유**: 놀이공원 자유이용권 — 매표소(IdP)에서 한 번만 사면 모든 놀이기구(SP)를 탈 수 있다

## 핵심 인사이트

1. **SSO는 "목표"이고, SAML/OAuth/OIDC는 "수단"**: SSO라는 개념을 구현하는 프로토콜이 여러 개 존재
2. **OAuth 2.0 단독으로는 SSO 불충분**: OAuth는 인가(Authorization)만 담당. 인증(Authentication)에는 OIDC 추가 필요
3. **OIDC가 신규 프로젝트 표준**: SAML은 레거시. 모바일/SPA는 OIDC 필수
4. **SSO ≠ 보안 완성**: 반드시 MFA와 함께 사용. SSO 계정 탈취 시 전체 서비스 노출 위험

## 관련 페이지

- [[sso-concept-explainer]] — 원본 (old_wiki)
- [[oauth1-concept-explainer]] — OAuth 1.0 Deep Dive
- [[oauth2-concept-explainer]] — OAuth 2.0 Deep Dive
- [[sso-oauth-comparison-and-architecture]] — SSO-OAuth 비교 + Google SSO 아키텍처
