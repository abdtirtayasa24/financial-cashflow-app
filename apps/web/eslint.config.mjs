import nextCoreWebVitals from "eslint-config-next/core-web-vitals";
import nextTypescript from "eslint-config-next/typescript";

// eslint-config-next v16 ships ready-to-use flat config arrays.
const eslintConfig = [...nextCoreWebVitals, ...nextTypescript];

export default eslintConfig;