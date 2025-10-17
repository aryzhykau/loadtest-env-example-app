{{/*
Expand the name of the chart.
*/}}
{{- define "loadtest-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "loadtest-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "loadtest-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "loadtest-app.labels" -}}
helm.sh/chart: {{ include "loadtest-app.chart" . }}
{{ include "loadtest-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "loadtest-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "loadtest-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Component specific labels
*/}}
{{- define "loadtest-app.componentLabels" -}}
{{ include "loadtest-app.labels" .root }}
app.kubernetes.io/component: {{ .component }}
{{- end }}

{{/*
Component selector labels
*/}}
{{- define "loadtest-app.componentSelectorLabels" -}}
{{ include "loadtest-app.selectorLabels" .root }}
app.kubernetes.io/component: {{ .component }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "loadtest-app.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "loadtest-app.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
MongoDB connection string
*/}}
{{- define "loadtest-app.mongodbUrl" -}}
{{- if .Values.mongodb.enabled -}}
mongodb://{{ include "loadtest-app.fullname" . }}-mongodb:{{ .Values.mongodb.service.port }}
{{- else -}}
{{ .Values.mongodb.externalUrl }}
{{- end -}}
{{- end -}}

{{/*
Redis connection string
*/}}
{{- define "loadtest-app.redisUrl" -}}
{{- if .Values.redis.enabled -}}
redis://{{ include "loadtest-app.fullname" . }}-redis:{{ .Values.redis.service.port }}/0
{{- else -}}
{{ .Values.redis.externalUrl }}
{{- end -}}
{{- end -}}
