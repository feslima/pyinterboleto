const PYPI_REPOSITORY = 'https://upload.pypi.org/legacy/';

const config = {
  branches: ['main'],
  plugins: [
    ['@semantic-release/commit-analyzer', { preset: 'conventionalcommits' }],
    '@semantic-release/release-notes-generator',
    [
      '@semantic-release/exec',
      {
        verifyConditionsCmd: `if [ 403 != $(curl -X POST -F ":action=file_upload" -u __token__:$PYPI_TOKEN -s -o /dev/null -w "%{http_code}" ${PYPI_REPOSITORY}) ]; then (exit 0); else (echo "Authentication error. Please check the PYPI_TOKEN environment variable." && exit 1); fi`,
        prepareCmd: 'poetry version ${nextRelease.version}',
        publishCmd: `poetry config repositories.repo ${PYPI_REPOSITORY} && poetry publish --build --repository repo --username __token__ --password $PYPI_TOKEN --no-interaction -vvv`,
      },
    ],
    [
      '@google/semantic-release-replace-plugin',
      {
        replacements: [
          {
            files: ['pyproject.toml'],
            ignore: ['test/*', 'tests/*'],
            from: 'version = ["\'].*["\']',
            to: 'version = "${nextRelease.version}"',
          },
        ],
      },
    ],
    [
      '@semantic-release/github',
      {
        assets: [
          { path: 'dist/*.tar.gz', label: 'sdist' },
          { path: 'dist/*.whl', label: 'wheel' },
        ],
      },
    ],
    [
      '@semantic-release/git',
      {
        assets: ['pyproject.toml'],
      },
    ],
  ],
};

module.exports = config;
