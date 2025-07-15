import { linkifyText, hasLinks } from './linkUtils';
import { registerDebugFunctions, onlyInDev } from './debugUtils';

/**
 * 링크 기능을 테스트하는 함수들
 */

// 테스트 케이스들
const testCases = [
  {
    name: '단일 링크',
    text: '웹사이트를 확인하세요: https://www.google.com',
  },
  {
    name: '여러 링크',
    text: 'Google: https://www.google.com 그리고 Naver: https://www.naver.com',
  },
  {
    name: '줄바꿈 포함',
    text: `첫 번째 줄: https://www.google.com
두 번째 줄: https://www.naver.com
세 번째 줄은 링크 없음`,
  },
  {
    name: 'HTTP와 HTTPS 혼합',
    text: 'HTTP: http://example.com 그리고 HTTPS: https://secure.example.com',
  },
  {
    name: '링크 없음',
    text: '이 텍스트에는 링크가 없습니다.',
  },
];

/**
 * 모든 테스트 케이스 실행
 */
export const runAllTests = () => {
  console.log('🧪 링크 기능 테스트 시작');
  console.log('='.repeat(50));

  testCases.forEach((testCase, index) => {
    console.log(`\n📝 테스트 ${index + 1}: ${testCase.name}`);
    console.log('입력:', testCase.text);

    // linkifyText 테스트
    const result = linkifyText(testCase.text);
    console.log('linkifyText 결과:', result);

    // hasLinks 테스트
    const hasLinksResult = hasLinks(testCase.text);
    console.log('hasLinks 결과:', hasLinksResult);

    console.log('-'.repeat(30));
  });

  console.log('\n✅ 모든 테스트 완료');
};

/**
 * URL 유효성 검증 함수
 */
const isValidUrl = (url: string): boolean => {
  try {
    const urlObj = new URL(url);
    return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
  } catch {
    return false;
  }
};

/**
 * URL 유효성 검증 테스트
 */
export const testUrlValidation = () => {
  const urls = [
    'https://www.google.com',
    'http://example.com',
    'ftp://ftp.example.com',
    'invalid-url',
    '',
    'https://',
  ];

  console.log('🔍 URL 유효성 검증 테스트');
  urls.forEach(url => {
    const isValid = isValidUrl(url);
    console.log(`"${url}" -> ${isValid ? '✅ 유효' : '❌ 무효'}`);
  });
};

/**
 * 통합 테스트 함수
 */
export const testLinkify = () => {
  runAllTests();
  testUrlValidation();
};

// 🔒 보안: 개발 환경에서만 전역 함수 등록
onlyInDev(() => {
  registerDebugFunctions({
    testLinksInConsole: testLinkify,
  });
});
