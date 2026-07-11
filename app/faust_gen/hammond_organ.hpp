/* ------------------------------------------------------------
name: "hammond_organ"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn HammondOrgan -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __HammondOrgan_H__
#define  __HammondOrgan_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS HammondOrgan
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

class HammondOrganSIG0 {
	
  private:
	
	int iVec0[2];
	int iRec0[2];
	
  public:
	
	int getNumInputsHammondOrganSIG0() {
		return 0;
	}
	int getNumOutputsHammondOrganSIG0() {
		return 1;
	}
	
	void instanceInitHammondOrganSIG0(int sample_rate) {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec0[l1] = 0;
		}
	}
	
	void fillHammondOrganSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec0[0] = 1;
			iRec0[0] = (iVec0[1] + iRec0[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec0[0]));
			iVec0[1] = iVec0[0];
			iRec0[1] = iRec0[0];
		}
	}

};

static HammondOrganSIG0* newHammondOrganSIG0() { return (HammondOrganSIG0*)new HammondOrganSIG0(); }
static void deleteHammondOrganSIG0(HammondOrganSIG0* dsp) { delete dsp; }

static float ftbl0HammondOrganSIG0[65536];

class HammondOrgan : public dsp {
	
 private:
	
	int iVec1[2];
	int fSampleRate;
	float fConst1;
	float fRec1[2];
	FAUSTFLOAT fHslider0;
	float fConst4;
	FAUSTFLOAT fButton0;
	float fVec2[2];
	int iRec3[2];
	float fConst5;
	float fConst6;
	float fConst7;
	int iRec4[2];
	float fVec3[2];
	float fConst8;
	float fConst9;
	float fRec2[2];
	FAUSTFLOAT fHslider1;
	int iRec5[2];
	float fConst10;
	float fRec6[2];
	float fConst11;
	FAUSTFLOAT fHslider2;
	float fConst12;
	float fRec7[2];
	float fConst13;
	float fRec8[2];
	FAUSTFLOAT fHslider3;
	float fConst14;
	float fRec9[2];
	float fConst15;
	float fRec10[2];
	float fConst16;
	float fRec11[2];
	float fConst17;
	float fRec12[2];
	FAUSTFLOAT fHslider4;
	int IOTA0;
	float fVec4[32];
	FAUSTFLOAT fHslider5;
	
 public:
	HammondOrgan() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn HammondOrgan -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("delays.lib/name", "Faust Delay Library");
		m->declare("delays.lib/version", "1.1.0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "hammond_organ.dsp");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "hammond_organ");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
		HammondOrganSIG0* sig0 = newHammondOrganSIG0();
		sig0->instanceInitHammondOrganSIG0(sample_rate);
		sig0->fillHammondOrganSIG0(65536, ftbl0HammondOrganSIG0);
		deleteHammondOrganSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		float fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 6.6f / fConst0;
		float fConst2 = std::tan(2827.4333f / fConst0);
		float fConst3 = 1.0f / fConst2;
		fConst4 = 1.0f - fConst3;
		fConst5 = std::max<float>(1.0f, 0.0004f * fConst0);
		fConst6 = 1.0f / fConst5;
		fConst7 = 1.0f / std::max<float>(1.0f, 0.007f * fConst0);
		fConst8 = 4.656613e-10f / fConst2;
		fConst9 = 1.0f / (fConst3 + 1.0f);
		fConst10 = 1.0f / std::max<float>(1.0f, 0.03f * fConst0);
		fConst11 = 1.0f / std::max<float>(1.0f, 0.004f * fConst0);
		fConst12 = 4.0f / fConst0;
		fConst13 = 3.0f / fConst0;
		fConst14 = 2.0f / fConst0;
		fConst15 = 1.0f / fConst0;
		fConst16 = 1.5f / fConst0;
		fConst17 = 0.5f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(0.5f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(0.4f);
		fHslider2 = FAUSTFLOAT(2.2e+02f);
		fHslider3 = FAUSTFLOAT(1.0f);
		fHslider4 = FAUSTFLOAT(1.0f);
		fHslider5 = FAUSTFLOAT(0.5f);
	}
	
	virtual void instanceClear() {
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iVec1[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec1[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fVec2[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec3[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			iRec4[l6] = 0;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fVec3[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec2[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			iRec5[l9] = 0;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec6[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec7[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fRec8[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fRec9[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 2; l14 = l14 + 1) {
			fRec10[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 2; l15 = l15 + 1) {
			fRec11[l15] = 0.0f;
		}
		for (int l16 = 0; l16 < 2; l16 = l16 + 1) {
			fRec12[l16] = 0.0f;
		}
		IOTA0 = 0;
		for (int l17 = 0; l17 < 32; l17 = l17 + 1) {
			fVec4[l17] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual HammondOrgan* clone() {
		return new HammondOrgan();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("hammond_organ");
		ui_interface->addHorizontalSlider("bright", &fHslider3, FAUSTFLOAT(1.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(2.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("click", &fHslider1, FAUSTFLOAT(0.4f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("leslie", &fHslider0, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("sub16", &fHslider4, FAUSTFLOAT(1.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(2.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		float fSlow1 = 0.28f * fSlow0;
		float fSlow2 = float(fButton0);
		float fSlow3 = 0.5f * float(fHslider1);
		int iSlow4 = fSlow2 == 0.0f;
		float fSlow5 = float(fHslider2);
		float fSlow6 = fConst12 * fSlow5;
		float fSlow7 = fConst13 * fSlow5;
		float fSlow8 = float(fHslider3);
		float fSlow9 = fConst14 * fSlow5;
		float fSlow10 = fConst15 * fSlow5;
		float fSlow11 = fConst16 * fSlow5;
		float fSlow12 = fConst17 * fSlow5;
		float fSlow13 = float(fHslider4);
		float fSlow14 = 4.5f * fSlow0;
		float fSlow15 = 0.45f * fSlow0;
		float fSlow16 = 1.0f - fSlow15;
		float fSlow17 = float(fHslider5);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec1[0] = 1;
			int iTemp0 = 1 - iVec1[1];
			float fTemp1 = ((iTemp0) ? 0.0f : fConst1 + fRec1[1]);
			fRec1[0] = fTemp1 - std::floor(fTemp1);
			float fTemp2 = ftbl0HammondOrganSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec1[0]), 65535))];
			fVec2[0] = fSlow2;
			iRec3[0] = (iRec3[1] + (iRec3[1] > 0)) * (fSlow2 <= fVec2[1]) + (fSlow2 > fVec2[1]);
			float fTemp3 = float(iRec3[0]);
			iRec4[0] = 1103515245 * iRec4[1] + 12345;
			float fTemp4 = float(iRec4[0]) * std::max<float>(0.0f, std::min<float>(fConst6 * fTemp3, fConst7 * (fConst5 - fTemp3) + 1.0f));
			fVec3[0] = fTemp4;
			fRec2[0] = fConst9 * (fConst8 * (fTemp4 - fVec3[1]) - fConst4 * fRec2[1]);
			iRec5[0] = iSlow4 * (iRec5[1] + 1);
			fRec6[0] = fSlow2 + fRec6[1] * float(fVec2[1] >= fSlow2);
			float fTemp5 = ((iTemp0) ? 0.0f : fSlow6 + fRec7[1]);
			fRec7[0] = fTemp5 - std::floor(fTemp5);
			float fTemp6 = ((iTemp0) ? 0.0f : fSlow7 + fRec8[1]);
			fRec8[0] = fTemp6 - std::floor(fTemp6);
			float fTemp7 = ((iTemp0) ? 0.0f : fSlow9 + fRec9[1]);
			fRec9[0] = fTemp7 - std::floor(fTemp7);
			float fTemp8 = ((iTemp0) ? 0.0f : fSlow10 + fRec10[1]);
			fRec10[0] = fTemp8 - std::floor(fTemp8);
			float fTemp9 = ((iTemp0) ? 0.0f : fSlow11 + fRec11[1]);
			fRec11[0] = fTemp9 - std::floor(fTemp9);
			float fTemp10 = ((iTemp0) ? 0.0f : fSlow12 + fRec12[1]);
			fRec12[0] = fTemp10 - std::floor(fTemp10);
			float fTemp11 = 0.2f * (fSlow13 * (0.5f * ftbl0HammondOrganSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec12[0]), 65535))] + 0.3f * ftbl0HammondOrganSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec11[0]), 65535))]) + ftbl0HammondOrganSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec10[0]), 65535))] + 0.55f * ftbl0HammondOrganSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec9[0]), 65535))] + fSlow8 * (0.3f * ftbl0HammondOrganSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec8[0]), 65535))] + 0.26f * ftbl0HammondOrganSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec7[0]), 65535))])) * std::max<float>(0.0f, std::min<float>(fConst11 * fRec6[0], 1.0f) * (1.0f - fConst10 * float(iRec5[0]))) + fSlow3 * fRec2[0];
			fVec4[IOTA0 & 31] = fTemp11;
			float fTemp12 = fSlow14 * (fTemp2 + 1.0f);
			float fTemp13 = fTemp12 + 14.0f;
			int iTemp14 = int(fTemp13);
			float fTemp15 = std::floor(fTemp13);
			float fTemp16 = tanhf(fSlow17 * (fSlow16 * fTemp11 + fSlow15 * (fVec4[(IOTA0 - std::min<int>(1025, std::max<int>(0, iTemp14))) & 31] * (fTemp15 + (-13.0f - fTemp12)) + (fTemp12 + (14.0f - fTemp15)) * fVec4[(IOTA0 - std::min<int>(1025, std::max<int>(0, iTemp14 + 1))) & 31])) * (fSlow1 * fTemp2 + 1.0f));
			output0[i0] = FAUSTFLOAT(fTemp16);
			output1[i0] = FAUSTFLOAT(fTemp16);
			iVec1[1] = iVec1[0];
			fRec1[1] = fRec1[0];
			fVec2[1] = fVec2[0];
			iRec3[1] = iRec3[0];
			iRec4[1] = iRec4[0];
			fVec3[1] = fVec3[0];
			fRec2[1] = fRec2[0];
			iRec5[1] = iRec5[0];
			fRec6[1] = fRec6[0];
			fRec7[1] = fRec7[0];
			fRec8[1] = fRec8[0];
			fRec9[1] = fRec9[0];
			fRec10[1] = fRec10[0];
			fRec11[1] = fRec11[0];
			fRec12[1] = fRec12[0];
			IOTA0 = IOTA0 + 1;
		}
	}

};

#endif
