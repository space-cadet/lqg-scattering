import { dirname, join, resolve } from 'path';
import { fileURLToPath } from 'url';

export const CODE_ROOT = dirname(fileURLToPath(import.meta.url));
export const PROJECT_ROOT = resolve(CODE_ROOT, '..');
export const MEMORY_BANK_DIR = join(PROJECT_ROOT, 'memory-bank');
export const MEMORY_BANK_DATABASE_DIR = join(MEMORY_BANK_DIR, 'database');
export const MEMORY_BANK_DATABASE_PATH = join(MEMORY_BANK_DATABASE_DIR, 'memory_bank.db');
