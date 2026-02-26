{{/*
차트 이름을 반환합니다.
.Chart.Name을 63자로 잘라 DNS 호환 이름을 생성합니다.
*/}}
{{- define "hello-world.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
풀네임을 반환합니다.
Release.Name-Chart.Name 조합을 63자로 잘라 고유한 리소스 이름을 생성합니다.
릴리즈 이름에 이미 차트 이름이 포함되어 있으면 릴리즈 이름만 사용합니다.
*/}}
{{- define "hello-world.fullname" -}}
{{- $name := .Chart.Name }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
공통 레이블을 반환합니다.
Kubernetes 권장 레이블 표준(app.kubernetes.io/*)을 따릅니다.
모든 리소스에 일관되게 적용하여 관리와 조회를 용이하게 합니다.
*/}}
{{- define "hello-world.labels" -}}
app.kubernetes.io/name: {{ include "hello-world.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
셀렉터 레이블을 반환합니다.
Deployment의 selector와 Service의 selector에 사용됩니다.
name + instance 조합으로 특정 릴리즈의 Pod를 정확히 선택합니다.
*/}}
{{- define "hello-world.selectorLabels" -}}
app.kubernetes.io/name: {{ include "hello-world.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
