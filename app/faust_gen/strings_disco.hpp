/* ------------------------------------------------------------
name: "strings_disco"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn StringsDisco -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __StringsDisco_H__
#define  __StringsDisco_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS StringsDisco
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

class StringsDiscoSIG0 {
	
  private:
	
	int iVec3[2];
	int iRec13[2];
	
  public:
	
	int getNumInputsStringsDiscoSIG0() {
		return 0;
	}
	int getNumOutputsStringsDiscoSIG0() {
		return 1;
	}
	
	void instanceInitStringsDiscoSIG0(int sample_rate) {
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			iVec3[l10] = 0;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			iRec13[l11] = 0;
		}
	}
	
	void fillStringsDiscoSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec3[0] = 1;
			iRec13[0] = (iVec3[1] + iRec13[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec13[0]));
			iVec3[1] = iVec3[0];
			iRec13[1] = iRec13[0];
		}
	}

};

static StringsDiscoSIG0* newStringsDiscoSIG0() { return (StringsDiscoSIG0*)new StringsDiscoSIG0(); }
static void deleteStringsDiscoSIG0(StringsDiscoSIG0* dsp) { delete dsp; }

static float StringsDisco_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0StringsDiscoSIG0[65536];

class StringsDisco : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fConst4;
	float fConst5;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec1[2];
	FAUSTFLOAT fHslider0;
	float fRec2[2];
	FAUSTFLOAT fHslider1;
	float fConst6;
	FAUSTFLOAT fHslider2;
	float fConst7;
	float fRec3[2];
	float fRec5[2];
	float fRec7[2];
	float fRec9[2];
	float fRec11[2];
	int IOTA0;
	float fVec2[8192];
	float fConst8;
	float fRec14[2];
	FAUSTFLOAT fHslider3;
	float fConst9;
	float fRec15[2];
	FAUSTFLOAT fHslider4;
	float fRec0[3];
	
 public:
	StringsDisco() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn StringsDisco -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("delays.lib/name", "Faust Delay Library");
		m->declare("delays.lib/version", "1.1.0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "strings_disco.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "strings_disco");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
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
		StringsDiscoSIG0* sig0 = newStringsDiscoSIG0();
		sig0->instanceInitStringsDiscoSIG0(sample_rate);
		sig0->fillStringsDiscoSIG0(65536, ftbl0StringsDiscoSIG0);
		deleteStringsDiscoSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(20420.352f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / StringsDisco_faustpower2_f(fConst1));
		float fConst3 = 1.0f / fConst1;
		fConst4 = (fConst3 + -1.4142135f) / fConst1 + 1.0f;
		fConst5 = 1.0f / ((fConst3 + 1.4142135f) / fConst1 + 1.0f);
		fConst6 = 0.15f / std::max<float>(1.0f, 0.3f * fConst0);
		fConst7 = 1.0f / fConst0;
		fConst8 = 0.53f / fConst0;
		fConst9 = 0.37f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.5f);
		fHslider1 = FAUSTFLOAT(0.09f);
		fHslider2 = FAUSTFLOAT(2.2e+02f);
		fHslider3 = FAUSTFLOAT(0.0035f);
		fHslider4 = FAUSTFLOAT(0.55f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec1[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec2[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec3[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec5[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec7[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec9[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec11[l8] = 0.0f;
		}
		IOTA0 = 0;
		for (int l9 = 0; l9 < 8192; l9 = l9 + 1) {
			fVec2[l9] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fRec14[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fRec15[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 3; l14 = l14 + 1) {
			fRec0[l14] = 0.0f;
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
	
	virtual StringsDisco* clone() {
		return new StringsDisco();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("strings_disco");
		ui_interface->addHorizontalSlider("attack", &fHslider1, FAUSTFLOAT(0.09f), FAUSTFLOAT(0.01f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.55f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("lush", &fHslider3, FAUSTFLOAT(0.0035f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.01f), FAUSTFLOAT(0.0001f));
		ui_interface->addHorizontalSlider("release", &fHslider0, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.05f), FAUSTFLOAT(2.5f), FAUSTFLOAT(0.001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow3 = std::max<float>(1.0f, fConst0 * float(fHslider1));
		float fSlow4 = 1.0f / fSlow3;
		float fSlow5 = float(fHslider2);
		float fSlow6 = std::max<float>(1.1920929e-07f, std::fabs(0.5015f * fSlow5));
		float fSlow7 = fConst7 * fSlow6;
		float fSlow8 = 1.0f - fConst0 / fSlow6;
		float fSlow9 = std::max<float>(1.1920929e-07f, std::fabs(0.4985f * fSlow5));
		float fSlow10 = fConst7 * fSlow9;
		float fSlow11 = 1.0f - fConst0 / fSlow9;
		float fSlow12 = std::max<float>(1.1920929e-07f, std::fabs(fSlow5));
		float fSlow13 = fConst7 * fSlow12;
		float fSlow14 = 1.0f - fConst0 / fSlow12;
		float fSlow15 = std::max<float>(1.1920929e-07f, std::fabs(0.996f * fSlow5));
		float fSlow16 = fConst7 * fSlow15;
		float fSlow17 = 1.0f - fConst0 / fSlow15;
		float fSlow18 = std::max<float>(1.1920929e-07f, std::fabs(1.004f * fSlow5));
		float fSlow19 = fConst7 * fSlow18;
		float fSlow20 = 1.0f - fConst0 / fSlow18;
		float fSlow21 = float(fHslider3);
		float fSlow22 = float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec1[0] = iSlow1 * (iRec1[1] + 1);
			fRec2[0] = fSlow0 + fRec2[1] * float(fVec1[1] >= fSlow0);
			float fTemp0 = fSlow7 + fRec3[1] + -1.0f;
			int iTemp1 = fTemp0 < 0.0f;
			float fTemp2 = fSlow7 + fRec3[1];
			fRec3[0] = ((iTemp1) ? fTemp2 : fTemp0);
			float fRec4 = ((iTemp1) ? fTemp2 : fSlow7 + fRec3[1] + fSlow8 * fTemp0);
			float fTemp3 = fSlow10 + fRec5[1] + -1.0f;
			int iTemp4 = fTemp3 < 0.0f;
			float fTemp5 = fSlow10 + fRec5[1];
			fRec5[0] = ((iTemp4) ? fTemp5 : fTemp3);
			float fRec6 = ((iTemp4) ? fTemp5 : fSlow10 + fRec5[1] + fSlow11 * fTemp3);
			float fTemp6 = fSlow13 + fRec7[1] + -1.0f;
			int iTemp7 = fTemp6 < 0.0f;
			float fTemp8 = fSlow13 + fRec7[1];
			fRec7[0] = ((iTemp7) ? fTemp8 : fTemp6);
			float fRec8 = ((iTemp7) ? fTemp8 : fSlow13 + fRec7[1] + fSlow14 * fTemp6);
			float fTemp9 = fSlow16 + fRec9[1] + -1.0f;
			int iTemp10 = fTemp9 < 0.0f;
			float fTemp11 = fSlow16 + fRec9[1];
			fRec9[0] = ((iTemp10) ? fTemp11 : fTemp9);
			float fRec10 = ((iTemp10) ? fTemp11 : fSlow16 + fRec9[1] + fSlow17 * fTemp9);
			float fTemp12 = fSlow19 + fRec11[1] + -1.0f;
			int iTemp13 = fTemp12 < 0.0f;
			float fTemp14 = fSlow19 + fRec11[1];
			fRec11[0] = ((iTemp13) ? fTemp14 : fTemp12);
			float fRec12 = ((iTemp13) ? fTemp14 : fSlow19 + fRec11[1] + fSlow20 * fTemp12);
			float fTemp15 = (2.0f * (fRec12 - (1.0f - (fRec10 + fRec8))) + 0.5f * (2.0f * fRec6 + -1.0f + 2.0f * fRec4 + -1.0f) + -1.0f) * std::max<float>(0.0f, std::min<float>(fSlow4 * fRec2[0], std::max<float>(fConst6 * (fSlow3 - fRec2[0]) + 1.0f, 0.85f)) * (1.0f - fSlow2 * float(iRec1[0])));
			fVec2[IOTA0 & 8191] = fTemp15;
			int iTemp16 = 1 - iVec0[1];
			float fTemp17 = ((iTemp16) ? 0.0f : fConst8 + fRec14[1]);
			fRec14[0] = fTemp17 - std::floor(fTemp17);
			float fTemp18 = fConst0 * (fSlow21 * ftbl0StringsDiscoSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec14[0]), 65535))] + 0.023f);
			int iTemp19 = int(fTemp18);
			float fTemp20 = std::floor(fTemp18);
			float fTemp21 = ((iTemp16) ? 0.0f : fConst9 + fRec15[1]);
			fRec15[0] = fTemp21 - std::floor(fTemp21);
			float fTemp22 = fConst0 * (fSlow21 * ftbl0StringsDiscoSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec15[0]), 65535))] + 0.016f);
			int iTemp23 = int(fTemp22);
			float fTemp24 = std::floor(fTemp22);
			fRec0[0] = fSlow22 * (0.15f * fTemp15 + 0.125f * (fVec2[(IOTA0 - std::min<int>(4097, std::max<int>(0, iTemp23))) & 8191] * (fTemp24 + (1.0f - fTemp22)) + (fTemp22 - fTemp24) * fVec2[(IOTA0 - std::min<int>(4097, std::max<int>(0, iTemp23 + 1))) & 8191] + fVec2[(IOTA0 - std::min<int>(4097, std::max<int>(0, iTemp19))) & 8191] * (fTemp20 + (1.0f - fTemp18)) + (fTemp18 - fTemp20) * fVec2[(IOTA0 - std::min<int>(4097, std::max<int>(0, iTemp19 + 1))) & 8191])) - fConst5 * (fConst4 * fRec0[2] + fConst2 * fRec0[1]);
			float fTemp25 = fConst5 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp25);
			output1[i0] = FAUSTFLOAT(fTemp25);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec1[1] = iRec1[0];
			fRec2[1] = fRec2[0];
			fRec3[1] = fRec3[0];
			fRec5[1] = fRec5[0];
			fRec7[1] = fRec7[0];
			fRec9[1] = fRec9[0];
			fRec11[1] = fRec11[0];
			IOTA0 = IOTA0 + 1;
			fRec14[1] = fRec14[0];
			fRec15[1] = fRec15[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
