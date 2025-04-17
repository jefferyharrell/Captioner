module.exports = {
  roots: ["<rootDir>/src"],
  testMatch: ["**/*.test.tsx"],
  testEnvironment: "jsdom",
  moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json", "node"],
  transform: {
    "^.+\\.(ts|tsx)$": ["ts-jest", { "tsconfig": "tsconfig.jest.json" }]
  },
  transformIgnorePatterns: ["/node_modules/"],
  moduleDirectories: ["node_modules", "src"],
  moduleNameMapper: {
    "\\.(css|less|scss|sass)$": "identity-obj-proxy",
    "^@/(.*)$": "<rootDir>/src/$1"
  },
  setupFilesAfterEnv: ["@testing-library/jest-dom"],
};
