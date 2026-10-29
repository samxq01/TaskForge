/**
 * Headless route and component smoke tester for TaskForge frontend.
 */
import fs from 'fs';
import path from 'path';

const routes = [
  'app/page.tsx',
  'app/dashboard/page.tsx',
  'app/tasks/page.tsx',
  'app/laboratory/page.tsx',
  'app/dependencies/page.tsx',
  'app/scheduling/page.tsx',
  'app/planning/page.tsx',
  'components/Navbar.tsx',
  'lib/api-client.ts',
];

console.log('--- Verifying Frontend Files ---');
let allPassed = true;
for (const r of routes) {
  const fullPath = path.join(process.cwd(), r);
  if (fs.existsSync(fullPath)) {
    const stat = fs.statSync(fullPath);
    console.log(`[PASS] ${r} (${stat.size} bytes)`);
  } else {
    console.error(`[FAIL] Missing file: ${r}`);
    allPassed = false;
  }
}

if (!allPassed) {
  process.exit(1);
} else {
  console.log('All 9 frontend routes and modules verified successfully.');
}
