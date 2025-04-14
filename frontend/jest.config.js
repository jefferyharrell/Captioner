module.exports = {
  testEnvironment: "jsdom",
  moduleNameMapper: {
    "\\.(css|less|scss|sass|svg|jpg|png)$": "identity-obj-proxy"
  },
  setupFilesAfterEnv: ["<rootDir>/jest.setup.js"],
  transform: {
    "^.+\\.(ts|tsx|js|jsx)$": ["ts-jest", { tsconfig: "tsconfig.jest.json" }]
  },

  transformIgnorePatterns: [
    "/node_modules/(?!(.*@testing-library.*|.*@babel.*|.*jest.*)/)"
  ]
};
