#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";

const repoRoot = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../../..");
const openapiPath = process.argv[2] || path.join(repoRoot, "sdk/openapi/agent2allow.openapi.json");
const outputPath = process.argv[3] || path.join(repoRoot, "sdk/js/openapi-types.d.ts");

function schemaToTs(schema) {
  if (!schema || typeof schema !== "object") return "unknown";
  if (schema.$ref) {
    const ref = String(schema.$ref);
    const parts = ref.split("/");
    return parts[parts.length - 1];
  }
  if (Array.isArray(schema.anyOf)) {
    return schema.anyOf.map(schemaToTs).join(" | ");
  }
  if (Array.isArray(schema.oneOf)) {
    return schema.oneOf.map(schemaToTs).join(" | ");
  }
  if (schema.type === "array") {
    return `Array<${schemaToTs(schema.items || {})}>`;
  }
  if (schema.type === "integer" || schema.type === "number") {
    return "number";
  }
  if (schema.type === "boolean") {
    return "boolean";
  }
  if (schema.type === "null") {
    return "null";
  }
  if (schema.type === "string") {
    return "string";
  }
  if (schema.type === "object" || schema.properties || schema.additionalProperties) {
    const properties = schema.properties || {};
    const required = new Set(schema.required || []);
    const entries = Object.entries(properties).map(([name, value]) => {
      const optional = required.has(name) ? "" : "?";
      return `  ${JSON.stringify(name)}${optional}: ${schemaToTs(value)};`;
    });
    if (entries.length === 0 && schema.additionalProperties) {
      if (schema.additionalProperties === true) return "Record<string, unknown>";
      return `Record<string, ${schemaToTs(schema.additionalProperties)}>`;
    }
    return `{\n${entries.join("\n")}\n}`;
  }
  return "unknown";
}

async function main() {
  const raw = await fs.readFile(openapiPath, "utf-8");
  const spec = JSON.parse(raw);
  const schemas = spec?.components?.schemas || {};

  const chunks = [];
  chunks.push("// Generated from OpenAPI. Do not edit manually.");
  chunks.push("");
  for (const [name, schema] of Object.entries(schemas)) {
    chunks.push(`export type ${name} = ${schemaToTs(schema)};`);
    chunks.push("");
  }
  chunks.push("export interface OpenAPIComponents {");
  chunks.push("  schemas: {");
  for (const name of Object.keys(schemas)) {
    chunks.push(`    ${name}: ${name};`);
  }
  chunks.push("  };");
  chunks.push("}");
  chunks.push("");

  await fs.writeFile(outputPath, chunks.join("\n"), "utf-8");
  console.log(`Wrote ${outputPath}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
