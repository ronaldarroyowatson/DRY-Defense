import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';

import { bootstrapDisplayCertificateLifecycle, readStoredDeviceCertificate } from '../../apps/display-runtime/src/lib/device-certificate.mjs';

function makeIssuedCertificate(id, subject) {
  return {
    certificate: {
      certificateId: id,
      subject,
      certificatePem: '-----BEGIN CERTIFICATE-----\nZXhhbXBsZQ==\n-----END CERTIFICATE-----\n',
      caChain: [
        '-----BEGIN CERTIFICATE-----\nY2hhaW4tMQ==\n-----END CERTIFICATE-----\n',
        '-----BEGIN CERTIFICATE-----\nY2hhaW4tMg==\n-----END CERTIFICATE-----\n'
      ],
      issuedAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + 60_000).toISOString(),
      rotationDueAt: new Date(Date.now() + 30_000).toISOString()
    },
    privateKeyPem: '-----BEGIN PRIVATE KEY-----\nZXhhbXBsZS1rZXk=\n-----END PRIVATE KEY-----\n'
  };
}

test('display runtime bootstraps and stores device certificate through command-service', async () => {
  const tempRoot = await fs.mkdtemp(path.join(os.tmpdir(), 'display-cert-test-'));
  const storePath = path.join(tempRoot, 'mempalace', 'secrets', 'device-certificate.json');
  const issued = makeIssuedCertificate('cert-1', 'display-runtime@test');
  const rotated = makeIssuedCertificate('cert-2', 'display-runtime@test');

  const callLog = [];
  let statusCalls = 0;

  const executeRoutedCommand = async (command, payload = {}) => {
    callLog.push({ command, payload });

    if (command === 'certificate.status') {
      statusCalls += 1;
      if (statusCalls === 1) {
        return { exists: false, rotateRequired: true, reason: 'missing' };
      }
      return {
        exists: true,
        rotateRequired: true,
        certificate: rotated.certificate,
        reason: 'expired-or-rotation-window'
      };
    }

    if (command === 'certificate.create') {
      return issued;
    }

    if (command === 'certificate.rotate') {
      return rotated;
    }

    throw new Error(`Unexpected command ${command}`);
  };

  const result = await bootstrapDisplayCertificateLifecycle({
    executeRoutedCommand,
    rootPath: tempRoot,
    subject: 'display-runtime@test',
    storePath,
    rotationPollMs: 35_000
  });

  assert.equal(result.subject, 'display-runtime@test');
  assert.equal(result.certificateId, 'cert-1');

  const stored = await readStoredDeviceCertificate(storePath);
  assert.equal(stored.certificateId, 'cert-1');
  assert.match(stored.privateKeyPem, /BEGIN PRIVATE KEY/);

  assert.equal(callLog[0].command, 'certificate.status');
  assert.equal(callLog[1].command, 'certificate.create');
});
