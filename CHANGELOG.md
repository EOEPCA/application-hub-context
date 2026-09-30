# Changelog

Notable changes to ApplicationHub Context, reconstructed from Git history through
`2222bcf` (2026-09-30). Release sections use the tags available in this repository;
dates are the tagged commits' dates. Changes between tags are consolidated, including
intermediate version bumps without corresponding tags. Merge and squash duplicates
are omitted. Tags `1.5.0` and `v1.5.0` identify the same commit.

## [Unreleased]

### Changed

- Use `external-secrets.io/v1` instead of `v1beta1` when creating and deleting
  ExternalSecret resources (`e8ce5f5`). Deployments must serve the `v1` API.
- Update configuration examples and documentation to use the standalone App Hub
  Configurator (`6d804aa`, #13).

### Removed

- Remove the bundled `apphub-configurator` package, its publishing workflow, and
  its Skaffold configuration-generation hook in favor of the standalone project
  (`6d804aa`, #13).

## [1.5.2] - 2026-01-27

### Changed

- Parse YAML before recursively rendering Jinja expressions in string values,
  preserving non-string values. Raise explicit errors for invalid YAML and
  configuration-processing failures (`8d66fe3`, #11).

### Fixed

- Correct the Kubernetes RoleBinding role reference API group and subject
  serialization (`e0cd533`, #12).
- Initialize `env_from` safely when importing environment variables from secrets,
  avoiding a missing-key error (`e0cd533`, #12).

## [1.5.1] - 2026-01-22

### Fixed

- Correct the upstream container image path to
  `ghcr.io/eoepca/container-k8s-hub:4.0.0` (`14cedd9`).

## [1.5.0] - 2026-01-21

This section consolidates changes since the `1.2.0` tag, including development
work from 2024 and 2025.

### Added

- Import environment variables from ConfigMaps and secrets, and mount secrets
  into application pods (`6b91432`, `3d71d27`, `da198ba`).
- Apply and clean up profile-defined manifests, including Crossplane Helm
  releases, Crossplane Kubernetes objects, and ExternalSecrets (`6f93dfc`,
  `8f8df19`, `74ff47d`).
- Render configuration values and resource names using Jinja templates with
  spawner context; expose the application namespace to configuration and manifest
  templates (`91b4ec7`, `975ff21`, `c23481c`).
- Support namespace labels and optional namespace checking and creation
  (`e797c92`, `ce8b1c9`).
- Support annotations on persistent volume claims (`823636c`, #6).
- Add the bundled App Hub Configurator, configuration-generation examples,
  documentation, and PyPI packaging (`cf31d40`, `6888fad`, #5).
- Add a configuration JSON schema and a task for generating Pydantic models
  (`60f57e4`, `07c63d8`).
- Add and revise Skaffold deployment profiles, including a custom configuration
  profile (`df9b441`, `f8c525b`).

### Changed

- Update the container for the 4.0.0 hub base and revise dependency installation
  (`13f6f61`, `d93164b`).
- Publish container images to GHCR with branch and release tags: `latest-dev` for
  `develop`, `latest` for `main`, and version tags for releases (`d93164b`,
  `67e360f`, `34f7aba`).
- Expand deployment, application configuration, and JupyterHub API documentation
  and examples (`71b0a70`, #7).

### Fixed

- Use the ConfigMap name when resolving environment-variable references
  (`68fb7e0`).
- Correct manifest persistence handling and empty environment-variable handling
  (`0ebeafe`, `d8ad8b7`, `ccd38b4`).
- Remove the hardcoded namespace from generated ExternalSecrets (`1b8af12`).
- Correct malformed URLs in the configuration schema (`c0bc6f4`, #8;
  `a246a37`, #9).
- Pin `configurable-http-proxy` and fix container publishing and CI configuration
  (`ca768e4`, `45b76db`, `34f7aba`).

### Removed

- Remove the old Helm chart (`89e7233`).
- Remove the development-container configuration and associated editor settings
  (`df9b441`).

## [1.2.0] - 2023-11-15

### Added

- Support image pull secrets and init containers in application profiles
  (`6e67a5d`).
- Document configuration of these features (`57b0571`, `1ff3344`).

## Earlier history - 2023-01-27 to 2023-09-19

These changes predate the earliest tag currently available (`1.2.0`). Earlier
version numbers occur in commit messages, but their tags are not present.

### Added

- Establish Kubernetes application contextualization, group-based profiles,
  configuration loading, volume handling, and ConfigMap management (`293bebb`,
  `9bf399f`, `28aa23f`).
- Provide ConfigMaps for Docker registry and S3 access (`5a727da`).
- Configure node selectors, CPU and memory requests, and additional resource
  limits and guarantees (`6ff3608`, `945b569`, `998f8a5`, `72b8247`).
- Populate environment variables from ConfigMap keys (`672ddfa`).
- Create and delete roles and role bindings for application profiles
  (`2d8a7a9`, `4a92403`).
- Document group management and obtaining JupyterHub API tokens (`bd30c3f`,
  `c20ef68`).

### Fixed

- Delete ConfigMaps marked as non-persistent (`680d53c`).
- Correct ConfigMap key lookup and handle missing ConfigMaps or keys (`e6d8fb9`,
  `86b06bb`, `7d4b868`).
- Correct role creation and role-binding cleanup (`1d502e2`, `573d347`).
- Use Python 3.9-compatible union type annotations (`2e3ff8d`).

[Unreleased]: https://github.com/EOEPCA/application-hub-context/compare/v1.5.2...HEAD
[1.5.2]: https://github.com/EOEPCA/application-hub-context/compare/v1.5.1...v1.5.2
[1.5.1]: https://github.com/EOEPCA/application-hub-context/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/EOEPCA/application-hub-context/compare/1.2.0...v1.5.0
[1.2.0]: https://github.com/EOEPCA/application-hub-context/releases/tag/1.2.0
